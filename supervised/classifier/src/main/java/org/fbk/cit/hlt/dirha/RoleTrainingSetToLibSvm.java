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

public class RoleTrainingSetToLibSvm {
	static Logger logger = Logger.getLogger(RoleTrainingSetToLibSvm.class.getName());

    public RoleTrainingSetToLibSvm( File featureFile, File instanceFile, File libsvnFile, File labelFile, File gazetteerFile ) throws IOException {
        logger.info( "processing " + instanceFile + "..." );
        PrintWriter pw = new PrintWriter( new BufferedWriter( new OutputStreamWriter( new FileOutputStream( libsvnFile ), "UTF-8" ) ) );
        FeatureIndex featureIndex = new FeatureIndex( );
        FeatureIndex labelIndex = new FeatureIndex( );

		// not in training set as we addMeasure it with custom rules
		labelIndex.put("Durata");
		labelIndex.put("Punteggio");
		labelIndex.put("Classifica");
		labelIndex.put("Tempo");
		labelIndex.put( "Squadra_1" );
		labelIndex.put( "Squadra_2" );

        Map<String, String> gazetteerMap = InputReader.ReadGazetteer( gazetteerFile );

        List<List<GenericToken>> sentencesList = InputReader.ReadSentences( instanceFile );
        RoleFeatureExtractor extractor = new RoleFeatureExtractor( featureIndex, gazetteerMap );

        for ( List<GenericToken> split : sentencesList ) {

            for ( int i = 0; i < split.size( ); i++ ) {
                GenericToken token = split.get( i );
                logger.trace( token.toString( ) );
                int label = labelIndex.put( token.getRole( ) );

                String featureVector = label + " " + extractor.extractFeatures( split, i );
                logger.trace( featureVector );
                pw.println( featureVector );
            }
        }

        pw.close( );
        featureIndex.write( new OutputStreamWriter( new FileOutputStream( featureFile ), "UTF-8" ) );
        labelIndex.write( new OutputStreamWriter( new FileOutputStream( labelFile ), "UTF-8" ) );

        logger.info( featureFile + " created" );
        logger.info( libsvnFile + " created" );
        logger.info( labelFile + " created" );
    }

	public static void main(String[] args) throws Exception {
		String logConfig = System.getProperty( "log-config" );
		if (logConfig == null) {
			logConfig = "log-config.txt";
		}

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

			PropertyConfigurator.configure(defaultProps);

			String training = line.getOptionValue("training");
			File featureFile = new File(training + ".iob2.feat");
			File exampleFile = new File(training);
			File libsvmFile = new File(training + ".iob2.svm");
			File labelFile = new File(training + ".iob2.label");

			File gazetteerFile = new File(line.getOptionValue("gazetteer"));
			new RoleTrainingSetToLibSvm(featureFile, exampleFile, libsvmFile, labelFile, gazetteerFile);
		} catch (ParseException e) {
			// oops, something went wrong
			System.out.println("Parsing failed: " + e.getMessage() + "\n");
			HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp(400, "java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.RoleTrainingSetToLibSvm", "\n", options, "\n", true);
		}
	}
}
