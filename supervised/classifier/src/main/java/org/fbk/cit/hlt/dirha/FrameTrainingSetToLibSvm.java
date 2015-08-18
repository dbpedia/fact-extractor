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
 *
 * java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.FrameTrainingSetToLibSvm dirha/data-frame-tagger/frasi-complete-0-100-400-100-claudio.tab.frame gazetteer.tsv
 *
 * time ~/Applications/libsvm-2.82/svm-train -t 0 -m 10000 frasi-complete-0-100-400-100-claudio.tab.frame.svm frasi-complete-0-100-400-100-claudio.tab.frame.mdl
 *
 *
 */
public class FrameTrainingSetToLibSvm {
    /**
     * Define a static logger variable so that it references the
     * Logger instance named <code>FrameTrainingSetToLibSvm</code>.
     */
    static Logger logger = Logger.getLogger(FrameTrainingSetToLibSvm.class.getName());

    File featureFile, instanceFile, libsvnFile, labelFile, gazetteerFile;
    FeatureIndex featureIndex, labelIndex;
    List<List<GenericToken>> sentenceList;
    Map<String, String> gazetteerMap;
    FrameFeatureExtractor extractor;

    public FrameTrainingSetToLibSvm( File featureFile, File instanceFile, File libsvnFile, File labelFile, File gazetteerFile ) throws IOException {
        this.featureFile = featureFile;
        this.instanceFile = instanceFile;
        this.libsvnFile = libsvnFile;
        this.labelFile = labelFile;
        this.gazetteerFile = gazetteerFile;

        sentenceList = InputReader.ReadSentences( instanceFile );
        gazetteerMap = InputReader.ReadGazetteer( gazetteerFile );

        featureIndex = new FeatureIndex( );
        labelIndex = new FeatureIndex( );
    }

    public void convert( ) throws IOException {
        logger.info( "processing " + instanceFile + "..." );
        PrintWriter pw = new PrintWriter( new BufferedWriter( new OutputStreamWriter( new FileOutputStream( libsvnFile ), "UTF-8" ) ) );
        extractor = new FrameFeatureExtractor( featureIndex, gazetteerMap );

       for(List<GenericToken> sentence: sentenceList ) {
            int label = labelIndex.put( sentence.get( 0 ).getFrame( ) );
            String featureVector = label + " " + extractor.extractFeatures( sentence );
            pw.println(featureVector);
        }

        // FIXME missing in training!!!
        labelIndex.put( "Vittoria" );
        labelIndex.put( "Partita" );
        labelIndex.put( "O" );

        pw.close( );
        featureIndex.write( new OutputStreamWriter( new FileOutputStream( featureFile ), "UTF-8" ) );
        labelIndex.write( new OutputStreamWriter( new FileOutputStream( labelFile ), "UTF-8" ) );

        logger.info( featureFile + " created" );
        logger.info( libsvnFile + " created" );
        logger.info( labelFile + " created" );
    }

    public static void main(String[] args) throws Exception {
        String logConfig = System.getProperty("log-config");
        if (logConfig == null) {
            logConfig = "log-config.txt";
        }

        Options options = new Options();
        try {
            options.addOption(OptionBuilder.withArgName("file").hasArg().withDescription("file from which to read the frame training file in 4-column format").isRequired().withLongOpt("training").create("t"));
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
            File featureFile = new File(training + ".frame.feat");
            File exampleFile = new File(training);
            File libsvmFile = new File(training + ".frame.svm");
            File labelFile = new File(training + ".frame.label");

            File gazetteerFile = new File(line.getOptionValue( "gazetteer" ));
            new FrameTrainingSetToLibSvm(featureFile, exampleFile, libsvmFile, labelFile, gazetteerFile).convert();
        } catch (ParseException e) {
            // oops, something went wrong
            System.out.println("Parsing failed: " + e.getMessage() + "\n");
            HelpFormatter formatter = new HelpFormatter();
            formatter.printHelp(400, "java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.FrameTrainingSetToLibSvm", "\n", options, "\n", true);
        }
    }
}
