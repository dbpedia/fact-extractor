package org.fbk.cit.hlt.dirha;

import org.apache.commons.cli.*;
import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;

import java.io.*;
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
 * Time: 11:29 AM
 * To change this template use File | Settings | File Templates.
 * <p/>
 * This class takes as input a file in IOB2 format and a gazetteer and returns
 * 3 files: (1) the example file in svmlib format; (2) the feature
 * file in tsv format; (c) the label file in tsv format
 * <p/>
 * java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.RoleTrainingSetToLibsvm -t data/whole-train/whole-train.tab.iob2 -g resources/gazetteer.tsv
 */
public class RoleTrainingSetToLibsvm {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>RoleTrainingSetToLibsvm</code>.
	 */
	static Logger logger = Logger.getLogger(RoleTrainingSetToLibsvm.class.getName());


	public RoleTrainingSetToLibsvm(File featureFile, File instanceFile, File libsvnFile, File labelFile, File gazetteerFile) throws IOException {
		logger.info("processing " + instanceFile + "...");
		PrintWriter pw = new PrintWriter(new BufferedWriter(new OutputStreamWriter(new FileOutputStream(libsvnFile), "UTF-8")));
		FeatureIndex featureIndex = new FeatureIndex();
		FeatureIndex labelIndex = new FeatureIndex();
		//featureIndex.readExampleList(new InputStreamReader(new FileInputStream(featureFile), "UTF-8"));
		List<ClassifierResults> exampleList = readExampleList(instanceFile);
		Map<String, String> gazetteerMap = readGazetteer(gazetteerFile);
		RoleFeatureExtraction roleFeatureExtraction = new RoleFeatureExtraction(featureIndex, exampleList, gazetteerMap);
		for (int i = 0; i < exampleList.size(); i++) {

			ClassifierResults example = exampleList.get(i);
			logger.trace(example.toString());
			int label = labelIndex.put(example.getLemma());

			//SortedSet<Integer> set = roleFeatureExtraction.extract(i);
			//String libsvmExample = label + " " + setToString(set);
			String libsvmExample = label + " " + roleFeatureExtraction.extractVector(i);
			logger.trace(libsvmExample);
			pw.println(libsvmExample);

		}
		pw.close();
		featureIndex.write(new OutputStreamWriter(new FileOutputStream(featureFile), "UTF-8"));
		labelIndex.write(new OutputStreamWriter(new FileOutputStream(labelFile), "UTF-8"));

		logger.info(featureFile + " created");
		logger.info(libsvnFile + " created");
		logger.info(labelFile + " created");

	}

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

	private List<ClassifierResults> readExampleList(File fin) throws IOException {
		List<ClassifierResults> list = new ArrayList<>();
		LineNumberReader lr = new LineNumberReader(new InputStreamReader(new FileInputStream(fin), "UTF-8"));

		String line = null;

		while ((line = lr.readLine()) != null) {
			String[] s = line.split("\\s+");
			list.add(new ClassifierResults( s[0], s[1], s[2], 0., 0., 0., -1, -1 ));
		}
		return list;
	}

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

	public static void main(String[] args) throws Exception {
		String logConfig = System.getProperty("log-config");
		if (logConfig == null) {
			logConfig = "log-config.txt";
		}
		/*PropertyConfigurator.configure(logConfig);
		if (args.length != 2) {
			logger.error("java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.RoleTrainingSetToLibsvm fin gazetteer");
			System.exit(-1);
		}*/


		Options options = new Options();
		try {
			options.addOption(OptionBuilder.withArgName("file").hasArg().withDescription("file from which to read the role training file in IOB2 format").isRequired().withLongOpt("training").create("t"));
			options.addOption(OptionBuilder.withArgName("file").hasArg().withDescription("file from which to read the gazetteer tsv format").isRequired().withLongOpt("gazetteer").create("g"));
			options.addOption(OptionBuilder.withDescription("trace mode").withLongOpt("trace").create());
			options.addOption(OptionBuilder.withDescription("debug mode").withLongOpt("debug").create());
			options.addOption("h", "help", false, "print this message");
			options.addOption("v", "version", false, "output version information and exit");


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

			String training = line.getOptionValue("training");
			File featureFile = new File(training + ".feat");
			File exampleFile = new File(training);
			File libsvmFile = new File(training + ".svm");
			File labelFile = new File(training + ".label");


			File gazetteerFile = new File(line.getOptionValue("gazetteer"));
			new RoleTrainingSetToLibsvm(featureFile, exampleFile, libsvmFile, labelFile, gazetteerFile);
		} catch (ParseException e) {
			// oops, something went wrong
			System.out.println("Parsing failed: " + e.getMessage() + "\n");
			HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp(400, "java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.RoleTrainingSetToLibsvm", "\n", options, "\n", true);
		}
	}
}
