package org.fbk.cit.hlt.dirha;

import org.annolab.tt4j.TreeTaggerWrapper;
import org.apache.commons.cli.*;
import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;
import org.fbk.cit.hlt.core.analysis.tokenizer.HardTokenizer;
import org.fbk.cit.hlt.core.analysis.tokenizer.Tokenizer;
import org.fbk.cit.hlt.core.mylibsvm.svm;
import org.fbk.cit.hlt.core.mylibsvm.svm_model;
import org.fbk.cit.hlt.core.mylibsvm.svm_node;
import org.fbk.cit.hlt.core.mylibsvm.svm_parameter;
import org.glassfish.grizzly.http.server.HttpServer;

import java.io.*;
import java.text.DecimalFormat;
import java.util.*;

/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

/**
 * Created with IntelliJ IDEA.
 * User: giuliano
 * Date: 10/14/13
 * Time: 3:46 PM
 * To change this template use File | Settings | File Templates.
 */
public class Annotator {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>Annotator</code>.
	 */
	static Logger logger = Logger.getLogger(Annotator.class.getName());

	public static final String DEFAULT_HOST = "localhost";

	DecimalFormat df = new DecimalFormat("###,###,###");

	public static final String DEFAULT_PORT = "8080";

	public static final String FRAME_NOT_FOUND_LABEL = "FRAME_NOT_FOUND";

	private svm_model roleModel;

	private svm_model frameModel;

	private Tokenizer tokenier;

	private TreeTaggerWrapper tt;

	FeatureIndex roleFeatureIndex;

	FeatureIndex roleLabelIndex;

	FeatureIndex frameFeatureIndex;

	FeatureIndex frameLabelIndex;

	private static DecimalFormat tf = new DecimalFormat("000,000,000.#");

	Map<String, String> gazetteerMap;
    private final ChunkCombinator combinator = new ChunkCombinator();

    public Annotator(String roleFile, String frameFile, File gazetteerFile, String lang) throws IOException {

		File roleFeatureFile = new File(roleFile + ".feat");
		File roleLibsvmModelFile = new File(roleFile + ".model");
		File roleLabelFile = new File(roleFile + ".label");

		tt = new TreeTaggerWrapper<String>();
		if (lang.equalsIgnoreCase("it")){
			tt.setModel(System.getProperty("treetagger.home") + "/lib/italian-utf8.par");
		} else if(lang.equalsIgnoreCase("en")){
			tt.setModel(System.getProperty("treetagger.home") + "/lib/english.par");
		} else if(lang.equalsIgnoreCase("de")){
			tt.setModel(System.getProperty("treetagger.home") + "/lib/german.par");
		}

		roleFeatureIndex = new FeatureIndex(true);
		roleFeatureIndex.read(new InputStreamReader(new FileInputStream(roleFeatureFile), "UTF-8"));
		logger.info(roleFeatureIndex.size() + " role features from " + roleFeatureFile);

		roleLabelIndex = new FeatureIndex(true);
		roleLabelIndex.read(new InputStreamReader(new FileInputStream(roleLabelFile), "UTF-8"));
		logger.info(roleLabelIndex.size() + " role labels " + roleLabelFile);

		File frameFeatureFile = new File(frameFile + ".feat");
		File frameLibsvmModelFile = new File(frameFile + ".model");
		File frameLabelFile = new File(frameFile + ".label");

		frameFeatureIndex = new FeatureIndex(true);
		frameFeatureIndex.read(new InputStreamReader(new FileInputStream(frameFeatureFile), "UTF-8"));
		logger.info(frameFeatureIndex.size() + " frame features from " + frameFeatureFile);

		frameLabelIndex = new FeatureIndex(true);
		frameLabelIndex.read(new InputStreamReader(new FileInputStream(frameLabelFile), "UTF-8"));
		logger.info(frameLabelIndex.size() + " frame labels from " + frameLabelFile);

		tokenier = new HardTokenizer();

		roleModel = svm.svm_load_model(roleLibsvmModelFile.getAbsolutePath());
		frameModel = svm.svm_load_model(frameLibsvmModelFile.getAbsolutePath());
		gazetteerMap = readGazetteer(gazetteerFile);

		//System.setProperty("treetagger.home", "/Users/giuliano/Applications/treetagger");
	}

	// todo: common
	private String setToString(SortedSet<Integer> set) {
		StringBuilder sb = new StringBuilder();
		Iterator<Integer> it = set.iterator();
		for (int i = 0; it.hasNext(); i++) {
			if (i > 0) {
				sb.append(" ");
			}
			int j = it.next();
			sb.append(j);
			sb.append(":1");
		}
		return sb.toString();
	}

	// todo: common
	private Map<String, String> readGazetteer(File fin) throws IOException {
		Map<String, String> map = new HashMap<String, String>();
		LineNumberReader lr = new LineNumberReader(new InputStreamReader(new FileInputStream(fin), "UTF-8"));

		String line = null;

		while ((line = lr.readLine()) != null) {
			String[] s = line.split("\\t+");
			for (int i = 1; i < s.length; i++) {
				map.put(s[i].toLowerCase(), s[0].toUpperCase());
			}
		}
		return map;
	}

	private List<String[]> readExampleList(Reader reader) throws IOException {
		List<String[]> list = new ArrayList<String[]>();
		//LineNumberReader lr = new LineNumberReader(new InputStreamReader(new FileInputStream(fin), "UTF-8"));
		LineNumberReader lr = new LineNumberReader(reader);

		String line = null;

		while ((line = lr.readLine()) != null) {
			String[] s = line.split("\\s+");
			list.add(s);
		}
		return list;
	}

	private List<String[]> toRoleExampleList(String line) throws Exception {

		List<String[]> exampleList = new ArrayList<String[]>();
		String[] eos = {"EOS", "EOS", "EOS"};
		exampleList.add(eos);

		//tt.setModel("/Users/giuliano/Applications/treetagger/lib/italian-utf8.par");
		/*if (System.getProperty("treetagger.home") == null) {
			tt.setModel("/Users/giuliano/Applications/treetagger/lib/italian-utf8.par");
		}
		else {
			tt.setModel(System.getProperty("treetagger.home") + "/lib/italian-utf8.par");
		} */
		try {
			TokenReader tokenReader = new TokenReader<String>(exampleList);

			tt.setHandler(tokenReader);

			//pw.println("sid\ttid\ttoken\tpos\tlemma\tframe\tLU/FE\tnotes\tstart/end time");
			String[] tokens = tokenier.stringArray(line);
			//logger.debug(Arrays.toString(tokens));
			tt.process(tokens);
		} catch (Exception e) {
			logger.error(e);
		}
        Map<String, String> disambiguated = combinator.getTheWikiMachineChunkToUri( line, true );
		exampleList = mergeChunksIntoExampleList(exampleList, disambiguated);
 		exampleList.add(eos);
		return exampleList;
	}

    private List<String[]> mergeChunksIntoExampleList( List<String[]> exampleList, Map<String, String> combinedChunks ) {
        List<String[]> merged = new ArrayList<>( exampleList );
        for ( String chunk : combinedChunks.keySet( ) ) {
            String[] tokens = chunk.split( "\\s+" );
            boolean found = false;
            int i = 0, j = 0;
            while ( i < merged.size( ) ) {
                String word = merged.get( i )[ 0 ];
                if ( tokens[ j ].equals( word ) ) {
                    j += 1;
                    if ( j == tokens.length ) {
                        found = true;
                        break;
                    }
                } else {
                    j = 0;
                }
                i += 1;
            }

            if ( found ) {
                List<String[]> tmpList = new ArrayList<>( );
                int matchStartIndex = i - tokens.length + 1;
                String[] toReplace = merged.get( i );
                String[] replacement;

                // Use the 'ENT' tag only if the n-gram has more than 1 token, otherwise keep the original POS tag
                if ( tokens.length > 1 )
                    replacement = new String[]{ chunk.replace( ' ', '_' ), "ENT", combinedChunks.get( chunk ) };
                else replacement = new String[]{ chunk, toReplace[ 1 ], combinedChunks.get( chunk ) };

                List<String[]> startSubList = merged.subList( 0, matchStartIndex );
                List<String[]> endSubList = merged.subList( i + 1, merged.size( ) );
                tmpList.addAll( startSubList );
                tmpList.add( replacement );
                tmpList.addAll( endSubList );
                merged = tmpList;
            }
        }
        return merged;
    }

	private List<String[]> toFrameExampleList(List<String[]> roleExampleList) throws Exception {
		List<String[]> exampleList = new ArrayList<String[]>();
		//String[] s = new String[1];
		//s[0] = "-1";
		//s[1] = "-1";
		Set<String> wordSet = new HashSet<String>();
		Set<String> lemmaSet = new HashSet<String>();
		Set<String> roleSet = new HashSet<String>();

		for (int i = 0; i < roleExampleList.size(); i++) {
			logger.debug(i + "\t" + Arrays.toString(roleExampleList.get(i)));
			String word = roleExampleList.get(i)[0];
			String lemma = roleExampleList.get(i)[2];
			if (!word.equalsIgnoreCase("EOS")) {
				wordSet.add(word);
				lemmaSet.add(lemma);

			}
			//wordSet.add(roleExampleList.get(i)[0]);
		}
		String[] s = new String[4];
		s[0] = "-1";
		s[1] = SpreadSheetToFrameTrainingSet.replace(wordSet.toString());
		s[2] = SpreadSheetToFrameTrainingSet.replace(lemmaSet.toString());
		exampleList.add(s);


		return exampleList;
	}

	private List<String> roleClassifier(List<String[]> roleExampleList) throws Exception {
		List<String> answerList = new ArrayList<String>(roleExampleList.size());
		//logger.debug(roleExampleList);
		RoleFeatureExtraction roleFeatureExtraction = new RoleFeatureExtraction(roleFeatureIndex, roleExampleList, gazetteerMap);
		for (int i = 0; i < roleExampleList.size(); i++) {

			String[] example = roleExampleList.get(i);
			logger.debug(example.length + "\t" + Arrays.toString(example));


			//SortedSet<Integer> set = roleFeatureExtraction.extract(i);
			//String libsvmExample =  "-1 " + setToString(set);
			String libsvmExample = "-1 " + roleFeatureExtraction.extractVector(i);
			logger.debug(libsvmExample);

			String y = predictRole(libsvmExample, 0);
			//logger.debug(y);
			String l = roleLabelIndex.getTerm((int) Double.parseDouble(y.trim()));
			//logger.info(l + "\t" + example[0]);
			logger.info(example[0] + "\t" + l + "\t"+y);
			//sb.append(example[0] + "\t" + l + "\n");
			answerList.add(l);
			//logger.debug("");
		}
		return answerList;
	}

	private List<String> frameClassifier(List<String[]> roleExampleList) throws Exception {
		List<String[]> frameExampleList = toFrameExampleList(roleExampleList);
		List<String> answerList = new ArrayList<String>(frameExampleList.size());
		FrameFeatureExtraction frameFeatureExtraction = new FrameFeatureExtraction(frameFeatureIndex, frameExampleList, gazetteerMap);
		for (int i = 0; i < frameExampleList.size(); i++) {
			String[] example = frameExampleList.get(i);
			logger.debug(i + "\t" + Arrays.toString(example));
			String libsvmExample = "-1 " + frameFeatureExtraction.extractVector(i);
			logger.debug(libsvmExample);

			String y = predictFrame(libsvmExample, 0);
			logger.debug(y);
			String l = frameLabelIndex.getTerm((int) Double.parseDouble(y.trim()));
			if (l == null) {
				l=FRAME_NOT_FOUND_LABEL;
			}
			logger.info(l + "\t" + example[0]);
			//sb.append(example[0] + "\t" + l + "\n");
			answerList.add(l);
		}
		return answerList;
	}

	public List<Answer> classify(File fin) throws IOException {
		List<Answer> list = new ArrayList<Answer>();
		LineNumberReader lr = new LineNumberReader(new FileReader(fin));
		String line = null;
		int count = 0;
		while ((line = lr.readLine()) != null) {
			try {
				if (line.length() > 0) {
					logger.debug(count + "\t" + line);
					/*List<String[]> roleExampleList = toRoleExampleList(line.trim());
					List<String> roleAnswerList = roleClassifier(roleExampleList);
					logger.debug(count + "\t" + roleAnswerList);
					List<String> frameAnswerList = frameClassifier(roleExampleList);
					logger.debug(count + "\t" + frameAnswerList);
					printAnswer(roleExampleList, roleAnswerList, frameAnswerList);
					list.add(new Answer(count, roleExampleList, roleAnswerList, frameAnswerList));  */
					list.add(classify(line, count));
					count++;
				}

			} catch (Exception e) {
				logger.error(e);
			}

		}
		return list;
	}

	public Answer classify(String line) throws Exception {
		//logger.debug("classifying " + line + "...");
		return classify(line, 0);
	}

	public Answer classify(String line, int count) throws Exception {
		logger.info("classifying " + line + " (" + count + ")...");
		List<String[]> roleExampleList = toRoleExampleList(line.trim());
		List<String> roleAnswerList = roleClassifier(roleExampleList);
		logger.debug(count + "\t" + roleAnswerList);
		List<String> frameAnswerList = frameClassifier(roleExampleList);
		logger.debug(count + "\t" + frameAnswerList);
		printAnswer(roleExampleList, roleAnswerList, frameAnswerList);
		return new Answer(count, roleExampleList, roleAnswerList, frameAnswerList);
	}

	private void printAnswer(List<String[]> roleExampleList, List<String> roleAnswerList, List<String> frameAnswerList) {
		logger.debug("===");
		logger.debug(roleExampleList.size());
		logger.debug(roleAnswerList.size());
		logger.debug(frameAnswerList.size());
		String frame = frameAnswerList.get(0);
		for (int i = 0; i < roleExampleList.size(); i++) {
			String[] example = roleExampleList.get(i);
			String role = roleAnswerList.get(i);
			if (role.equalsIgnoreCase("O")) {
				logger.info(i + "\tO\t" + role + "\t" + Arrays.toString(example));
			}
			else {
				logger.info(i + "\t" + frame + "\t" + role + "\t" + Arrays.toString(example));
			}

		}
		logger.debug("+++");
	}

	public void interactive() throws Exception {
		InputStreamReader isr = null;
		BufferedReader myInput = null;
		long begin = 0, end = 0;
		while (true) {
			System.out.println("\nPlease write a sentence and type <return> to continue (CTRL C to exit):");
			isr = new InputStreamReader(System.in);
			myInput = new BufferedReader(isr);
			String query = myInput.readLine().toString();
			begin = System.nanoTime();

			StringBuilder sb = new StringBuilder();
			sb.append(query + "\n");
			List<String[]> roleExampleList = toRoleExampleList(query);
			logger.debug(roleExampleList);
			//todo: put outside the while, add a setRoleExampleList in RoleFeatureExtraction...
			RoleFeatureExtraction roleFeatureExtraction = new RoleFeatureExtraction(roleFeatureIndex, roleExampleList, gazetteerMap);
			for (int i = 0; i < roleExampleList.size(); i++) {

				String[] example = roleExampleList.get(i);
				logger.debug(example.length + "\t" + Arrays.toString(example));


				//SortedSet<Integer> set = roleFeatureExtraction.extract(i);
				//String libsvmExample =  "-1 " + setToString(set);
				String libsvmExample = "-1 " + roleFeatureExtraction.extractVector(i);
				logger.debug(libsvmExample);

				String y = predictRole(libsvmExample, 0);
				logger.debug(y);
				String l = roleLabelIndex.getTerm((int) Double.parseDouble(y.trim()));
				//logger.info(l + "\t" + example[0]);
				logger.info(example[0] + "\t" + l);
				sb.append(example[0] + "\t" + l + "\n");
				logger.debug("");
			}

			List<String[]> frameExampleList = toFrameExampleList(roleExampleList);
			//todo: put outside the while, add a setFrameExampleList in FrameFeatureExtraction...
			FrameFeatureExtraction frameFeatureExtraction = new FrameFeatureExtraction(frameFeatureIndex, frameExampleList, gazetteerMap);
			for (int i = 0; i < frameExampleList.size(); i++) {
				String[] example = frameExampleList.get(i);
				logger.debug(i + "\t" + Arrays.toString(example));
				String libsvmExample = "-1 " + frameFeatureExtraction.extractVector(i);
				logger.debug(libsvmExample);

				String y = predictFrame(libsvmExample, 0);
				logger.debug(y);
				String l = frameLabelIndex.getTerm((int) Double.parseDouble(y.trim()));
				logger.info(l + "\t" + example[0]);
				sb.append(example[0] + "\t" + l + "\n");
			}

			logger.info(sb.toString());

			end = System.nanoTime();
			//logger.info("query\tdf\tlf\tratio\ttime");
			logger.info("done in " + tf.format(end - begin) + " ns");
		}
	}

	private static double atof(String s) {
		return Double.valueOf(s).doubleValue();
	}

	private static int atoi(String s) {
		return Integer.parseInt(s);
	}

	private String predictRole(String line, int predict_probability) throws IOException {

		StringBuilder sb = new StringBuilder();
		int correct = 0;
		int total = 0;
		double error = 0;
		double sumv = 0, sumy = 0, sumvv = 0, sumyy = 0, sumvy = 0;

		int svm_type = svm.svm_get_svm_type(roleModel);
		int nr_class = svm.svm_get_nr_class(roleModel);
		double[] prob_estimates = null;

		if (predict_probability == 1) {
			if (svm_type == svm_parameter.EPSILON_SVR ||
					svm_type == svm_parameter.NU_SVR) {
				logger.info("Prob. roleModel for test data: target value = predicted value + z,\nz: Laplace distribution e^(-|z|/sigma)/(2sigma),sigma=" + svm.svm_get_svr_probability(roleModel) + "\n");
			}
			else {
				int[] labels = new int[nr_class];
				svm.svm_get_labels(roleModel, labels);
				prob_estimates = new double[nr_class];
				sb.append("labels");
				for (int j = 0; j < nr_class; j++) {
					sb.append(" " + labels[j]);
				}
				sb.append("\n");
			}
		}

		{

			if (line == null) {
				return "";
			}

			StringTokenizer st = new StringTokenizer(line, " \t\n\r\f:");

			double target = atof(st.nextToken());
			int m = st.countTokens() / 2;
			svm_node[] x = new svm_node[m];
			for (int j = 0; j < m; j++) {
				x[j] = new svm_node();
				x[j].index = atoi(st.nextToken());
				x[j].value = atof(st.nextToken());
			}
			logger.debug(svm_node.toString(x));
			double v;
			if (predict_probability == 1 && (svm_type == svm_parameter.C_SVC || svm_type == svm_parameter.NU_SVC)) {
				v = svm.svm_predict_probability(roleModel, x, prob_estimates);
				sb.append(v + " ");
				for (int j = 0; j < nr_class; j++) {
					sb.append(prob_estimates[j] + " ");
				}
				sb.append("\n");
			}
			else {
				// original
				v = svm.svm_predict(roleModel, x);
				//sb.append(v + "\n");
				sb.append(v);
			}

			if (v == target) {
				++correct;
			}
			error += (v - target) * (v - target);
			sumv += v;
			sumy += target;
			sumvv += v * v;
			sumyy += target * target;
			sumvy += v * target;
			++total;
		}
		if (svm_type == svm_parameter.EPSILON_SVR ||
				svm_type == svm_parameter.NU_SVR) {
			logger.debug("Mean squared error = " + error / total + " (regression)");
			logger.debug("Squared correlation coefficient = " +
					((total * sumvy - sumv * sumy) * (total * sumvy - sumv * sumy)) /
							((total * sumvv - sumv * sumv) * (total * sumyy - sumy * sumy)) +
					" (regression)");
		}
		else {
			logger.debug("Accuracy = " + (double) correct / total * 100 +
					"% (" + correct + "/" + total + ") (classification)");
		}

		return sb.toString();
	}

	private String predictFrame(String line, int predict_probability) throws IOException {

		StringBuilder sb = new StringBuilder();
		int correct = 0;
		int total = 0;
		double error = 0;
		double sumv = 0, sumy = 0, sumvv = 0, sumyy = 0, sumvy = 0;

		int svm_type = svm.svm_get_svm_type(frameModel);
		int nr_class = svm.svm_get_nr_class(frameModel);
		double[] prob_estimates = null;

		if (predict_probability == 1) {
			if (svm_type == svm_parameter.EPSILON_SVR ||
					svm_type == svm_parameter.NU_SVR) {
				logger.info("Prob. roleModel for test data: target value = predicted value + z,\nz: Laplace distribution e^(-|z|/sigma)/(2sigma),sigma=" + svm.svm_get_svr_probability(roleModel) + "\n");
			}
			else {
				int[] labels = new int[nr_class];
				svm.svm_get_labels(frameModel, labels);
				prob_estimates = new double[nr_class];
				sb.append("labels");
				for (int j = 0; j < nr_class; j++) {
					sb.append(" " + labels[j]);
				}
				sb.append("\n");
			}
		}

		{

			if (line == null) {
				return "";
			}

			StringTokenizer st = new StringTokenizer(line, " \t\n\r\f:");

			double target = atof(st.nextToken());
			int m = st.countTokens() / 2;
			svm_node[] x = new svm_node[m];
			for (int j = 0; j < m; j++) {
				x[j] = new svm_node();
				x[j].index = atoi(st.nextToken());
				x[j].value = atof(st.nextToken());
			}
			logger.debug(svm_node.toString(x));
			double v;
			if (predict_probability == 1 && (svm_type == svm_parameter.C_SVC || svm_type == svm_parameter.NU_SVC)) {
				v = svm.svm_predict_probability(frameModel, x, prob_estimates);
				sb.append(v + " ");
				for (int j = 0; j < nr_class; j++) {
					sb.append(prob_estimates[j] + " ");
				}
				sb.append("\n");
			}
			else {
				// original
				v = svm.svm_predict(frameModel, x);
				//sb.append(v + "\n");
				sb.append(v);
			}

			if (v == target) {
				++correct;
			}
			error += (v - target) * (v - target);
			sumv += v;
			sumy += target;
			sumvv += v * v;
			sumyy += target * target;
			sumvy += v * target;
			++total;
		}
		if (svm_type == svm_parameter.EPSILON_SVR ||
				svm_type == svm_parameter.NU_SVR) {
			logger.debug("Mean squared error = " + error / total + " (regression)\n");
			logger.debug("Squared correlation coefficient = " +
					((total * sumvy - sumv * sumy) * (total * sumvy - sumv * sumy)) /
							((total * sumvv - sumv * sumv) * (total * sumyy - sumy * sumy)) +
					" (regression)\n");
		}
		else {
			logger.debug("Accuracy = " + (double) correct / total * 100 +
					"% (" + correct + "/" + total + ") (classification)\n");
		}

		return sb.toString();
	}

	public void write(List<Answer> list, File fout, String format) throws IOException {
		PrintWriter pw = new PrintWriter(new BufferedWriter(new OutputStreamWriter(new FileOutputStream(fout), "UTF-8")));
		for (int i = 0; i < list.size(); i++) {
			Answer answer = list.get(i);
			if (format.equalsIgnoreCase("tsv")) {
				pw.print(answer.toTSV());
			}

		}
		pw.close();
	}

	public static void main(String[] args) throws Exception {

		String logConfig = System.getProperty("log-config");
		if (logConfig == null) {
			logConfig = "log-config.txt";
		}
		//PropertyConfigurator.configure(logConfig);
		/*if (args.length != 2) {
			logger.error("java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.Annotator spreadsheet.tab gaz.tsv");
			System.exit(-1);
		}*/
		Options options = new Options();
		try {
			Option inputFileOpt = OptionBuilder.withArgName("file").hasArg().withDescription("root of files from which to read the frame and role models").isRequired().withLongOpt("model").create("m");
			Option gazetteerFileOpt = OptionBuilder.withArgName("file").hasArg().withDescription("gazetteer file").isRequired().withLongOpt("gazetteer").create("g");
			Option evalFileOpt = OptionBuilder.withArgName("file").hasArg().withDescription("evaluation (annotated gold) spreadsheet file in tsv format)").withLongOpt("eval").create("e");
			Option reportFileOpt = OptionBuilder.withArgName("file").hasArg().withDescription("file in which to write the evaluation report in tsv format").withLongOpt("report").create("r");
			Option classifyFileOpt = OptionBuilder.withArgName("file").hasArg().withDescription("annotate offline the specified file in one sentence per line format").withLongOpt("annotate").create("a");
			Option outputFileOpt = OptionBuilder.withArgName("file").hasArg().withDescription("file in which to write the annotated the offline annotation in tsv format").withLongOpt("output").create("o");
			Option interactiveModeOpt = OptionBuilder.withDescription("enter in the interactive mode").withLongOpt("interactive-mode").create("i");
			Option serverOpt = OptionBuilder.withDescription("start the server").withLongOpt("server").create("s");
			Option hostOpt = OptionBuilder.withArgName("url").hasArg().withDescription("server name (default name is " + DEFAULT_HOST + ")").withLongOpt("host").create();
			Option portOpt = OptionBuilder.withArgName("int").hasArg().withDescription("server port (default name is " + DEFAULT_PORT + ")").withLongOpt("port").create();
			Option langOpt = OptionBuilder.withArgName("string").hasArg().withDescription("language").isRequired().withLongOpt("lang").create("l");

			options.addOption(OptionBuilder.withDescription("trace mode").withLongOpt("trace").create());
			options.addOption(OptionBuilder.withDescription("debug mode").withLongOpt("debug").create());


			//Option roleExtractionOpt = OptionBuilder.withDescription("extract roles").withLongOpt("role-extraction").create("r");
			//Option frameExtractionOpt = OptionBuilder.withDescription("extract frames").withLongOpt("frame-extraction").create("f");
			//Option crossValidationOpt = OptionBuilder.withArgName("int").hasArg().withDescription("run n-fold cross-validation").withLongOpt("n-fold").create("n");
			//Option libsvmOpt = OptionBuilder.withDescription("use the libsvm c").withLongOpt("use-c").create("c");

			options.addOption("h", "help", false, "print this message");
			options.addOption("v", "version", false, "output version information and exit");


			options.addOption(inputFileOpt);
			options.addOption(interactiveModeOpt);
			options.addOption(evalFileOpt);
			options.addOption(gazetteerFileOpt);
			options.addOption(classifyFileOpt);
			options.addOption(outputFileOpt);
			options.addOption(reportFileOpt);
			options.addOption(serverOpt);
			options.addOption(hostOpt);
			options.addOption(portOpt);
			options.addOption(langOpt);

			CommandLineParser parser = new PosixParser();
			CommandLine line = parser.parse(options, args);

			Properties defaultProps = new Properties();
			defaultProps.load(new InputStreamReader(new FileInputStream(logConfig), "UTF-8"));
			//defaultProps.setProperty("log4j.rootLogger", "info,stdout");
			if (line.hasOption("trace")) {
				defaultProps.setProperty("log4j.rootLogger", "trace,stdout");
			}
			else if (line.hasOption("debug")) {
				defaultProps.setProperty("log4j.rootLogger", "debug,stdout");
			}
			else if (logConfig == null) {
				defaultProps.setProperty("log4j.rootLogger", "info,stdout");
			}
			PropertyConfigurator.configure(defaultProps);

			File gazetteerFile = new File(line.getOptionValue("gazetteer"));
			String iob2 = line.getOptionValue("model") + ".iob2";
			String frame = line.getOptionValue("model") + ".frame";
			String lang = line.getOptionValue("lang");


			Annotator annotator = new Annotator(iob2, frame, gazetteerFile, lang);
			if (line.hasOption("interactive-mode")) {
				annotator.interactive();
			}

			if (line.hasOption("server")) {
				String host = line.getOptionValue("host");
				if (host == null) {
					host = DEFAULT_HOST;
				}
				String port = line.getOptionValue("port");
				if (port == null) {
					port = DEFAULT_PORT;
				}

				HttpServer httpServer = HttpServer.createSimpleServer(host, new Integer(port).intValue());
				httpServer.getServerConfiguration().addHttpHandler(new AnnotationHttpHandler(annotator, host, port, lang), "/tu");

				long end = System.currentTimeMillis();
				logger.debug("starting " + host + "\t" + port + "...");
				try {
					httpServer.start();
					Thread.currentThread().join();
				} catch (Exception e) {
					logger.error("error running " + host + ":" + port);
					logger.error(e);
				}
			}

			if (line.hasOption("annotate")) {
				File textFile = new File(line.getOptionValue("annotate"));
				List<Answer> list = annotator.classify(textFile);
				File fout = null;

				if (line.hasOption("output")) {
					fout = new File(line.getOptionValue("output"));
				}
				else {
					//fout = File.createTempFile("dirha", new Date().toString());
					fout = new File(textFile.getAbsoluteFile() + ".output.tsv");
				}
				File evaluationReportFile = null;
				if (line.hasOption("report")) {
					evaluationReportFile = new File(line.getOptionValue("report"));
				}
				else {
					evaluationReportFile = new File(textFile.getAbsoluteFile() + ".report.tsv");
				}
				logger.info("output file: " + fout);
				if (line.hasOption("format")) {
					annotator.write(list, fout, line.getOptionValue("format"));
				}
				else {
					annotator.write(list, fout, "tsv");
				}

				if (line.hasOption("eval")) {
					File evalFile = new File(line.getOptionValue("eval"));
					Evaluator evaluator = new Evaluator(evalFile, fout);
					evaluator.write(evaluationReportFile);
				}

			}

		} catch (ParseException e) {
			// oops, something went wrong
			System.out.println("Parsing failed: " + e.getMessage() + "\n");
			HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp(400, "java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.Annotator", "\n", options, "\n", true);
		}

	}

}
