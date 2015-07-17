package org.fbk.cit.hlt.dirha;

import org.apache.commons.cli.*;
import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;

import java.io.*;
import java.util.Properties;

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
 * Date: 10/4/13
 * Time: 5:06 PM
 * To change this template use File | Settings | File Templates.
 * <p/>
 * This class takes as input an annotated file and returns a
 * file annotated in IOB2 format to train a role classifier.
 * <p/>
 * java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.SpreadSheetToRoleTrainingSet dirha/data-frame-tagger/frasi-complete-0-100-400-100-claudio.tab dirha/data-frame-tagger/frasi-complete-0-100-400-100-claudio.iob2
 */
public class SpreadSheetToRoleTrainingSet {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>SpreadSheetToRoleTrainingSet</code>.
	 */
	static Logger logger = Logger.getLogger(SpreadSheetToRoleTrainingSet.class.getName());

	public SpreadSheetToRoleTrainingSet(File fin, File fout) throws IOException {
		logger.info("processing " + fin + "...");
		LineNumberReader lr = new LineNumberReader(new InputStreamReader(new FileInputStream(fin), "UTF-8"));
		PrintWriter pw = new PrintWriter(new BufferedWriter(new OutputStreamWriter(new FileOutputStream(fout), "UTF-8")));
		String line = null;

		while ((line = lr.readLine()) != null) {
			String[] s = line.split("\t");
			if (s.length > 5) {
				logger.trace(line);
				if (s[0].matches("\\d+")) {
					//if (s.length > 6) {
					//if(!s[6].equals("O")) {
					pw.println(s[2] + " " + s[3] + " " + s[4] + " " + s[6]);
					//} else {
					//	pw.println(s[2] + " " + s[3] + " " + s[4] + " O");
					//}
					//}
				}
				else {
					pw.println("EOS EOS EOS O");
				}
			} else{
				pw.println("EOS EOS EOS O");
			}

		}
		pw.println("EOS EOS EOS O");
		pw.close();
		logger.info(fout +" created");
	}

	public static void main(String[] args) throws Exception {
		String logConfig = System.getProperty("log-config");
		if (logConfig == null) {
			logConfig = "log-config.txt";
		}

		Options options = new Options();
		try {
			options.addOption(OptionBuilder.withArgName("file").hasArg().withDescription("file from which to read the role training file in tab format").isRequired().withLongOpt("training").create("t"));
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
			new SpreadSheetToRoleTrainingSet(new File(training), new File(training + ".iob2"));
		} catch (ParseException e) {
			// oops, something went wrong
			System.out.println("Parsing failed: " + e.getMessage() + "\n");
			HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp(400, "java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.SpreadSheetToRoleTrainingSet", "\n", options, "\n", true);
		}
	}
}
