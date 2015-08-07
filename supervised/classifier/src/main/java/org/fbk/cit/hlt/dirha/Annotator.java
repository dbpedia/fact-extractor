package org.fbk.cit.hlt.dirha;

import org.annolab.tt4j.TokenHandler;
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
        ClassifierResults.RoleLabelList = roleLabelIndex;

		File frameFeatureFile = new File(frameFile + ".feat");
		File frameLibsvmModelFile = new File(frameFile + ".model");
		File frameLabelFile = new File(frameFile + ".label");

		frameFeatureIndex = new FeatureIndex(true);
		frameFeatureIndex.read(new InputStreamReader(new FileInputStream(frameFeatureFile), "UTF-8"));
		logger.info(frameFeatureIndex.size() + " frame features from " + frameFeatureFile);

		frameLabelIndex = new FeatureIndex(true);
		frameLabelIndex.read(new InputStreamReader(new FileInputStream(frameLabelFile), "UTF-8"));
		logger.info(frameLabelIndex.size() + " frame labels from " + frameLabelFile);
        ClassifierResults.FrameLabelList = frameLabelIndex;

		tokenier = new HardTokenizer();

		roleModel = svm.svm_load_model(roleLibsvmModelFile.getAbsolutePath());
		frameModel = svm.svm_load_model(frameLibsvmModelFile.getAbsolutePath());
		gazetteerMap = readGazetteer(gazetteerFile);
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

    private List<ClassifierResults> toRoleExampleList( String line ) throws Exception {

        final List<ClassifierResults> exampleList = new ArrayList<>( );
        ClassifierResults eos = new ClassifierResults( "EOS", "EOS", "EOS", 0., 0., 0., -1, -1 );
        exampleList.add( eos );

        try {
            tt.setHandler( new TokenHandler( ) {
                @Override
                public void token( Object token, String pos, String lemma ) {
                    exampleList.add( new ClassifierResults( ( String ) token, pos, lemma, 1., 0., 0., -1, -1 ) );
                }
            } );

            String[] tokens = tokenier.stringArray( line );
            tt.process( tokens );
        }
        catch ( Exception e ) {
            logger.error( e );
        }
        Map<String, ChunkCombinator.ChunkToUri> disambiguated = combinator.getTheWikiMachineChunkToUriWithConfidence( line, true );
        List<ClassifierResults> merged = mergeChunksIntoExampleList( exampleList, disambiguated );
        merged.add( eos );
        return merged;
    }

    private List<ClassifierResults> mergeChunksIntoExampleList( List<ClassifierResults> exampleList, Map<String,
            ChunkCombinator.ChunkToUri> combinedChunks ) {

        List<ClassifierResults> merged = new ArrayList<>( exampleList );
        for ( String chunk : combinedChunks.keySet( ) ) {
            String[] tokens = chunk.split( "\\s+" );
            boolean found = false;
            int i = 0, j = 0;
            while ( i < merged.size( ) ) {
                String word = merged.get( i ).getToken( );
                if ( tokens[ j ].equals( word ) ) {
                    j += 1;
                    if ( j == tokens.length ) {
                        found = true;
                        break;
                    }
                }
                else {
                    j = 0;
                }
                i += 1;
            }

            if ( found ) {
                List<ClassifierResults> tmpList = new ArrayList<>( );
                int matchStartIndex = i - tokens.length + 1;
                ClassifierResults toReplace = merged.get( i );
                ClassifierResults replacement;

                // Use the 'ENT' tag only if the n-gram has more than 1 token, otherwise keep the original POS tag
                if ( tokens.length > 1 ) {
                    replacement = new ClassifierResults( chunk.replace( ' ', '_' ), "ENT",
                                                         combinedChunks.get( chunk ).getUri( ),
                                                         combinedChunks.get( chunk ).getConfidence( ),
                                                         toReplace.getFrameConfidence( ),
                                                         toReplace.getRoleConfidence( ),
                                                         toReplace.getPredictedRole( ),
                                                         toReplace.getPredictedFrame( ) );
                }
                else {
                    replacement = new ClassifierResults( chunk, toReplace.getPos( ),
                                                         combinedChunks.get( chunk ).getUri( ),
                                                         combinedChunks.get( chunk ).getConfidence( ),
                                                         toReplace.getFrameConfidence( ),
                                                         toReplace.getRoleConfidence( ),
                                                         toReplace.getPredictedRole( ),
                                                         toReplace.getPredictedFrame( ) );
                }

                List<ClassifierResults> startSubList = merged.subList( 0, matchStartIndex );
                List<ClassifierResults> endSubList = merged.subList( i + 1, merged.size( ) );
                tmpList.addAll( startSubList );
                tmpList.add( replacement );
                tmpList.addAll( endSubList );
                merged = tmpList;
            }
        }
        return merged;
    }

    private void classifyRoles( List<ClassifierResults> classifierResultsList ) throws Exception {
        RoleFeatureExtraction roleFeatureExtraction = new RoleFeatureExtraction( roleFeatureIndex,
                                                                                 classifierResultsList,
                                                                                 gazetteerMap );

        Map<Integer, Double> probabilities = new HashMap<>( );
        for ( int i = 0; i < classifierResultsList.size( ); i++ ) {
            ClassifierResults example = classifierResultsList.get( i );
            logger.debug( example.toString( ) );

            String libsvmExample = "-1 " + roleFeatureExtraction.extractVector( i );
            logger.debug( libsvmExample );

            int y = predict( libsvmExample, roleModel, true, probabilities );
            example.setPredictedRole( y );
            example.setRoleConfidence( probabilities.get( y ) );
            logger.info( example.getToken( ) + "\t" + y );
        }
    }

    private void classifyFrames( List<ClassifierResults> classifierResultsList ) throws Exception {
        String[] example = toFrameExample( classifierResultsList );
        List<String[]> frameExampleList = new ArrayList<String[]>();
        frameExampleList.add( example );
        FrameFeatureExtraction frameFeatureExtraction = new FrameFeatureExtraction( frameFeatureIndex,
                                                                                    frameExampleList,
                                                                                    gazetteerMap );
		Map<Integer, Double> probabilities = new HashMap<>( );
        logger.debug( Arrays.toString( example ) );
        String libsvmExample = "-1 " + frameFeatureExtraction.extractVector( 0 );
        logger.debug( libsvmExample );

        int y = predict( libsvmExample, frameModel, true, probabilities );
        for ( ClassifierResults cr : classifierResultsList ) {
            cr.setPredictedFrame( y );
            cr.setFrameConfidence( probabilities.get( y ) );
        }
    }

    private String[] toFrameExample( List<ClassifierResults> classifierResultsList ) throws Exception {
        Set<String> wordSet = new HashSet<>();
        Set<String> lemmaSet = new HashSet<>();
        Set<String> roleSet = new HashSet<>();

        for (int i = 0; i < classifierResultsList.size(); i++) {
            logger.debug(i + "\t" + classifierResultsList.get(i).toString( ));
            String word = classifierResultsList.get( i ).getToken( );
            String lemma = classifierResultsList.get( i ).getLemma( );
            if (!word.equalsIgnoreCase("EOS")) {
                wordSet.add(word);
                lemmaSet.add(lemma);

            }
            //wordSet.add(classifierResultsList.get(i)[0]);
        }
        String[] s = new String[4];
        s[0] = "-1";
        s[1] = SpreadSheetToFrameTrainingSet.replace(wordSet.toString());
        s[2] = SpreadSheetToFrameTrainingSet.replace(lemmaSet.toString());

        return s;
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
					List<String> roleAnswerList = classifyRoles(roleExampleList);
					logger.debug(count + "\t" + roleAnswerList);
					List<String> frameAnswerList = classifyFrames(roleExampleList);
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
		List<ClassifierResults> classifierResultsList = toRoleExampleList(line.trim());
		classifyRoles( classifierResultsList );
		classifyFrames( classifierResultsList );
		printAnswer( classifierResultsList );
		return new Answer(count, classifierResultsList );
	}

	private void printAnswer(List<ClassifierResults> classifierResultsList ) {
		logger.debug("===");
		logger.debug( classifierResultsList.size());
		String frame = classifierResultsList.get(0).getPredictedFrameLabel();
		for (int i = 0; i < classifierResultsList.size(); i++) {
			ClassifierResults example = classifierResultsList.get(i);
			String role = classifierResultsList.get(i).getPredictedRoleLabel();
			if (role.equalsIgnoreCase("O")) {
				logger.info(i + "\tO\t" + role + "\t" + example.toString( ) );
			}
			else {
				logger.info(i + "\t" + frame + "\t" + role + "\t" + example.toString( ) );
			}

		}
		logger.debug("+++");
	}

	public void interactive() throws Exception {
		InputStreamReader isr = null;
		BufferedReader myInput = null;
		long begin = 0, end = 0;
		while (true) {
			System.out.println("\nPlease write a sentence and pos <return> to continue (CTRL C to exit):");
			isr = new InputStreamReader(System.in);
			myInput = new BufferedReader(isr);
			String query = myInput.readLine().toString();
			begin = System.nanoTime();

			StringBuilder sb = new StringBuilder();
			sb.append(query + "\n");
			List<ClassifierResults> classifierResultsList = toRoleExampleList(query);
			logger.debug( classifierResultsList );
			//todo: put outside the while, add a setRoleExampleList in RoleFeatureExtraction...
			RoleFeatureExtraction roleFeatureExtraction = new RoleFeatureExtraction(roleFeatureIndex, classifierResultsList, gazetteerMap);
			for (int i = 0; i < classifierResultsList.size(); i++) {

				ClassifierResults example = classifierResultsList.get(i);
				logger.debug( example.toString( ) );


				//SortedSet<Integer> set = roleFeatureExtraction.extract(i);
				//String libsvmExample =  "-1 " + setToString(set);
				String libsvmExample = "-1 " + roleFeatureExtraction.extractVector(i);
				logger.debug(libsvmExample);

				int y = predict( libsvmExample, roleModel, false, null );
				logger.debug(y);
				String l = roleLabelIndex.getTerm(y);
				//logger.info(l + "\t" + example[0]);
				logger.info(example.getToken( ) + "\t" + l);
				sb.append(example.getToken( ) + "\t" + l + "\n");
				logger.debug("");
			}

            //todo: put outside the while, add a setFrameExampleList in FrameFeatureExtraction...
			String[] frameExample= toFrameExample( classifierResultsList );
            List<String[]> frameExampleList = new ArrayList<String[]>();
            frameExampleList.add( frameExample );
			FrameFeatureExtraction frameFeatureExtraction = new FrameFeatureExtraction(frameFeatureIndex,
                                                                                       frameExampleList,
                                                                                       gazetteerMap);

            logger.debug(Arrays.toString(frameExample));
            String libsvmExample = "-1 " + frameFeatureExtraction.extractVector(0);
            logger.debug(libsvmExample);

            int y = predict( libsvmExample, frameModel, false, null );
            logger.debug( y );
            String l = frameLabelIndex.getTerm(y);
            logger.info(l + "\t" + frameExample[0]);
            sb.append(frameExample[0] + "\t" + l + "\n");

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

    private int predict(String line, svm_model model, boolean predict_probability,
                               Map<Integer, Double> probabilities) throws IOException {
        if (line == null) return -1;

        int correct = 0;
        int total = 0;
        double error = 0;
        double sumv = 0, sumy = 0, sumvv = 0, sumyy = 0, sumvy = 0;

		int svm_type = svm.svm_get_svm_type(model);
		int nr_class = svm.svm_get_nr_class(model);

        if (predict_probability && (svm_type == svm_parameter.EPSILON_SVR ||
                svm_type == svm_parameter.NU_SVR)) {
            logger.info("Prob. model for test data: target value = predicted value + z,");
            logger.info("z: Laplace distribution e^(-|z|/sigma)/(2sigma),sigma=" + svm.svm_get_svr_probability(roleModel));
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
        if (predict_probability && (svm_type == svm_parameter.C_SVC || svm_type == svm_parameter.NU_SVC)) {
            double[] prob_estimates = new double[nr_class];
            v = svm.svm_predict_probability(model, x, prob_estimates);
            for(int i = 0; i  < prob_estimates.length; i++)
                probabilities.put(i, prob_estimates[i]);
        }
        else v = svm.svm_predict(model, x);

        if (v == target) correct += 1;
        error += (v - target) * (v - target);
        sumv += v;
        sumy += target;
        sumvv += v * v;
        sumyy += target * target;
        sumvy += v * target;
        ++total;

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

        return ( int ) v;
    }

	public void write(List<Answer> list, File fout, File confidences_out, String format) throws IOException {
        PrintWriter pw_answer = new PrintWriter( new BufferedWriter( new OutputStreamWriter(
                new FileOutputStream( fout ), "UTF-8" ) ) );
        PrintWriter pw_conf = new PrintWriter( new BufferedWriter( new OutputStreamWriter(
                new FileOutputStream( confidences_out ), "UTF-8" ) ) );

        for ( int i = 0; i < list.size( ); i++ ) {
            Answer answer = list.get( i );
            if ( format.equalsIgnoreCase( "tsv" ) ) {
                pw_answer.print( answer.toTSV( ) );
                pw_conf.print( answer.confidenceToTSV( ) );
            }
        }
        pw_answer.close( );
        pw_conf.close( );
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
            Option confOutOpt =OptionBuilder.withArgName("file").hasArg().withDescription("file in which to write the confidence of annotated results").withLongOpt("conf-output").create( "c" );
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
            options.addOption( confOutOpt );

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
				File fout = null, confOut = null;

				if (line.hasOption("output"))
					fout = new File(line.getOptionValue("output"));
				else fout = new File(textFile.getAbsoluteFile() + ".output.tsv");

                if ( line.hasOption( "conf-output" ) )
                    confOut = new File( line.getOptionValue( "conf-output" ) );
                else confOut = new File( textFile.getAbsoluteFile( ) + ".confidence.output.tsv" );

				File evaluationReportFile = null;
				if (line.hasOption("report")) {
					evaluationReportFile = new File(line.getOptionValue("report"));
				}
				else {
					evaluationReportFile = new File(textFile.getAbsoluteFile() + ".report.tsv");
				}
				logger.info("output file: " + fout);
                logger.info("confidence file: " + confOut);
				if (line.hasOption("format")) {
					annotator.write(list, fout, confOut, line.getOptionValue("format"));
				}
				else {
					annotator.write(list, fout, confOut, "tsv");
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
