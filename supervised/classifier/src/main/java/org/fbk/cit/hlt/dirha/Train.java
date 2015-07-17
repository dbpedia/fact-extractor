package org.fbk.cit.hlt.dirha;

import org.apache.commons.cli.*;
import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;
import org.fbk.cit.hlt.core.mylibsvm.svm_train;

import java.io.File;
import java.io.IOException;
import java.util.Arrays;

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
 * Time: 3:58 PM
 * To change this template use File | Settings | File Templates.
 */
public class Train {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>Train</code>.
	 */
	static Logger logger = Logger.getLogger(Train.class.getName());

	public static void main(String[] args) throws IOException {

		String logConfig = System.getProperty("log-config");
		if (logConfig == null) {
			logConfig = "log-config.txt";
		}
		PropertyConfigurator.configure(logConfig);

		/*if (args.length != 2) {
			logger.error("java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.Train fin gazetteer");
			System.exit(-1);
		}*/

		Options options = new Options();
		try {
			Option inputFileOpt = OptionBuilder.withArgName("file").hasArg().withDescription("annotated spreadsheet file in tsv format").isRequired().withLongOpt("spreadsheet").create("s");
			Option gazetteerFileOpt = OptionBuilder.withArgName("file").hasArg().withDescription("gazetteer file").isRequired().withLongOpt("gazetteer").create("g");
			Option roleExtractionOpt = OptionBuilder.withDescription("extract roles").withLongOpt("role-extraction").create("r");
			Option frameExtractionOpt = OptionBuilder.withDescription("extract frames").withLongOpt("frame-extraction").create("f");
			Option crossValidationOpt = OptionBuilder.withArgName("int").hasArg().withDescription("run n-fold cross-validation").withLongOpt("n-fold").create("n");
			Option libsvmOpt = OptionBuilder.withDescription("use the libsvm c").withLongOpt("use-c").create("c");

			options.addOption("h", "help", false, "print this message");
			options.addOption("v", "version", false, "output version information and exit");


			options.addOption(inputFileOpt);
			options.addOption(roleExtractionOpt);
			options.addOption(frameExtractionOpt);
			options.addOption(gazetteerFileOpt);
			options.addOption(crossValidationOpt);
			options.addOption(libsvmOpt);

			CommandLineParser parser = new PosixParser();
			CommandLine line = parser.parse(options, args);

			//logger.debug(line.hasOption("n-fold"));
			//logger.debug(line.getOptionValue("n-fold"));
			//System.exit(0);
			File fin = new File(line.getOptionValue("spreadsheet"));
			File gazetteerFile = new File(line.getOptionValue("gazetteer"));


			if (line.hasOption("role-extraction")) {

				File iob2 = new File(line.getOptionValue("spreadsheet") + ".iob2");
				logger.info("converting " + fin + " in iob2 format " + iob2 + "...");
				new SpreadSheetToRoleTrainingSet(fin, iob2);


				File roleFeatureFile = new File(iob2.getAbsolutePath() + ".feat");
				File roleLibsvmFile = new File(iob2.getAbsolutePath() + ".svm");
				File roleLabelFile = new File(iob2.getAbsolutePath() + ".label");
				File roleModelLabelFile = new File(iob2.getAbsolutePath() + ".model");
				logger.info("converting " + iob2 + " in libsvm format " + roleLibsvmFile + "...");
				new RoleTrainingSetToLibsvm(roleFeatureFile, iob2, roleLibsvmFile, roleLabelFile, gazetteerFile);

				logger.info("converting " + iob2 + " in libsvm format " + roleLibsvmFile + "...");
				String[] parameters = null;
				if (line.hasOption("n-fold")) {
					parameters = new String[5];
					parameters[0] = "-t";
					parameters[1] = "0";
					parameters[2] = "-v";
					parameters[3] = line.getOptionValue("n-fold");
					parameters[4] = roleLibsvmFile.getAbsolutePath();
				} else {
					parameters = new String[4];
					parameters[0] = "-t";
					parameters[1] = "0";
					parameters[2] = roleLibsvmFile.getAbsolutePath();
					parameters[3] = roleModelLabelFile.getAbsolutePath();
				}
				logger.info("training a svm " + Arrays.toString(parameters));
				if (line.hasOption("use-c")) {
					new LibsvmWrapper(parameters);
				} else {
					new svm_train().main(parameters);
				}


			}

			if (line.hasOption("frame-extraction")) {
				File frame = new File(line.getOptionValue("spreadsheet") + ".frame");

				new SpreadSheetToFrameTrainingSet(fin, frame);

				File frameFeatureFile = new File(frame.getAbsolutePath() + ".feat");
				File frameLibsvmFile = new File(frame.getAbsolutePath() + ".svm");
				File frameLabelFile = new File(frame.getAbsolutePath() + ".label");
				File frameModelLabelFile = new File(frame.getAbsolutePath() + ".model");
				new FrameTrainingSetToLibsvm(frameFeatureFile, frame, frameLibsvmFile, frameLabelFile, gazetteerFile);
				String[] parameters = null;
				if (line.hasOption("n-fold")) {
					parameters = new String[5];
					parameters[0] = "-t";
					parameters[1] = "0";
					parameters[2] = "-v";
					parameters[3] = line.getOptionValue("n-fold");
					parameters[4] = frameLibsvmFile.getAbsolutePath();
				} else {
					parameters = new String[4];
					parameters[0] = "-t";
					parameters[1] = "0";
					parameters[2] = frameLibsvmFile.getAbsolutePath();
					parameters[3] = frameModelLabelFile.getAbsolutePath();
				}
				logger.info("training a svm " + Arrays.toString(parameters));
				if (line.hasOption("use-c")) {
					new LibsvmWrapper(parameters);
				} else {
					new svm_train().main(parameters);
				}
			}
		} catch (ParseException e) {
			// oops, something went wrong
			System.out.println("Parsing failed: " + e.getMessage() + "\n");
			HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp(400, "java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.Train", "\n", options, "\n", true);
		}
	}
}
