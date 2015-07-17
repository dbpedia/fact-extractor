package org.fbk.cit.hlt.dirha;

import org.apache.commons.cli.*;
import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;

import java.io.*;
import java.util.HashSet;
import java.util.Properties;
import java.util.Set;

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
 * Time: 9:42 AM
 * To change this template use File | Settings | File Templates.
 * <p/>
 * This class takes as input an annotated file and returns a
 * file annotated in BOW format to train a frame classifier.
 *
 * German needs all terms!
 *
 * <p/>
 * java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.SpreadSheetToFrameTrainingSet dirha/data-frame-tagger/frasi-complete-0-100-400-100-claudio.tab dirha/data-frame-tagger/frasi-complete-0-100-400-100-claudio.tab.frame
 */
public class SpreadSheetToFrameTrainingSet {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>SpreadSheetToFrameTrainingSet</code>.
	 */
	static Logger logger = Logger.getLogger(SpreadSheetToFrameTrainingSet.class.getName());

	public SpreadSheetToFrameTrainingSet(File fin, File fout) throws IOException {
		logger.info("processing " + fin + "...");
		LineNumberReader lr = new LineNumberReader(new InputStreamReader(new FileInputStream(fin), "UTF-8"));
		PrintWriter pw = new PrintWriter(new BufferedWriter(new OutputStreamWriter(new FileOutputStream(fout), "UTF-8")));
		String line = null;

		Set<String> wordSet = new HashSet<String>();
		Set<String> lemmaSet = new HashSet<String>();
		Set<String> roleSet = new HashSet<String>();
		String frame = null;

		while ((line = lr.readLine()) != null) {
			String[] s = line.split("\t");
			if (s.length >= 5) {
				logger.trace(line);
				//if (s[0].matches("\\d+") && (s[6].equalsIgnoreCase("B-LU") || s[6].equalsIgnoreCase("I-LU")))
				// only terms with role are used?
				//if (s[0].matches("\\d+") && !s[6].equalsIgnoreCase("O")) {
					wordSet.add(s[2]);
					lemmaSet.add(s[4]);
					if (!s[5].equals("")) {
						frame = s[5];
					}

					roleSet.add(s[6]);

				//}
			}
            if (frame != null) {
                pw.println(frame + "\t" + replace(wordSet.toString()) + "\t" + replace(lemmaSet.toString()) + "\t" + replace(roleSet.toString()));
            }

            wordSet = new HashSet<String>();
            lemmaSet = new HashSet<String>();
            roleSet = new HashSet<String>();
            frame = null;

		}
		pw.close();
		logger.info(fout +" created");
	}

	public static String replace(String s) {

		String t = s.substring(1, s.length() - 1).toLowerCase();
		t = t.replace(", ", " ");
		t = t.replace("|", " ");
		return t;
	}



	public static void main(String[] args) throws Exception {
		String logConfig = System.getProperty("log-config");
		if (logConfig == null) {
			logConfig = "log-config.txt";
		}

		Options options = new Options();
		try {
			options.addOption(OptionBuilder.withArgName("file").hasArg().withDescription("file from which to read the frame training file in tab format").isRequired().withLongOpt("training").create("t"));
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


			File fin = new File(training);
			File fout = new File(training + ".frame");
			new SpreadSheetToFrameTrainingSet(fin, fout);


		} catch (ParseException e) {
			// oops, something went wrong
			System.out.println("Parsing failed: " + e.getMessage() + "\n");
			HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp(400, "java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.SpreadSheetToFrameTrainingSet", "\n", options, "\n", true);
		}
	}
}
