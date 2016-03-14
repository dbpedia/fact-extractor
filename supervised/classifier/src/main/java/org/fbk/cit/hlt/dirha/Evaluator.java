package org.fbk.cit.hlt.dirha;

import net.razorvine.pickle.objects.SetConstructor;
import org.apache.commons.cli.*;
import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;
import org.fbk.cit.hlt.dirha.kernel.SysGoldAligner;

import java.io.*;
import java.text.DecimalFormat;
import java.util.*;
import java.util.List;

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
 * Date: 11/26/13
 * Time: 4:03 PM
 * To change this template use File | Settings | File Templates.
 */
public class Evaluator {

    /**
     * Keeps track of true positives/false positives/false negatives
     * and computes precision/recall/f1
     */
    class Evaluation {
        private int tp;
        private int fp;
        private int fn;

        Evaluation( ) {
            this( 0, 0, 0 );
        }

        Evaluation( int tp, int fp, int fn ) {
            this.tp = tp;
            this.fp = fp;
            this.fn = fn;
        }

        void incTp( ) {
            tp++;
        }

        void incFp( ) {
            fp++;
        }

        void incFn( ) {
            fn++;
        }

        void addTp( int n ) {
            tp += n;
        }

        void addFn( int n ) {
            fn += n;
        }

        void addFp( int n ) {
            fp += n;
        }

        int getFn( ) {
            return fn;
        }

        void setFn( int fn ) {
            this.fn = fn;
        }

        int getFp( ) {
            return fp;
        }

        void setFp( int fp ) {
            this.fp = fp;
        }

        int getTp( ) {
            return tp;
        }

        void setTp( int tp ) {
            this.tp = tp;
        }

        double precision( ) {
            return ( double ) tp / ( tp + fp );
        }

        double recall( ) {
            return ( double ) tp / ( tp + fn );
        }

        double f1( ) {
            return ( 2 * precision( ) * recall( ) ) / ( precision( ) + recall( ) );
        }

        @Override
        public String toString( ) {
            return tp + "\t" + fp + "\t" + fn + "\t" + ( tp + fn ) + "\t" +
                    df.format( precision( ) ) + "\t" + df.format( recall( ) ) + "\t" + df.format( f1( ) );
        }
    }

    /**
     * Used to check whether two FEs should be considered the same using sets
     * wraps Role instances
     */
    class RoleComparer {
        Role role;
        boolean strict;

        public RoleComparer( Role role, boolean strict ) {
            this.role = role;
            this.strict = strict;
        }

        public boolean equals( Object otherComparer ) {
            Role other = ( ( RoleComparer ) otherComparer ).role;

            if ( strict ) {
                return role.getName( ).equals( other.getName( ) ) &&
                        role.getValue( ).toLowerCase( ).equals( other.getValue( ).toLowerCase( ) );
            }
            else {
                String val1 = role.getValue( ).toLowerCase( ),
                        val2 = other.getValue( ).toLowerCase( );

                return role.getName( ).equals( other.getName( ) ) &&
                        ( val1.contains( val2 ) || val2.contains( val1 ) );
            }
        }

        public int hashCode( ) {
            return 0;
        }
    }

    static Logger logger = Logger.getLogger( Evaluator.class.getName( ) );

    private File goldFile;
    private File testFile;

    protected static DecimalFormat df = new DecimalFormat( "0.00" );

    Evaluation frameEvaluation;
    Evaluation roleEvaluation;

    FeatureIndex frameLabels;
    FeatureIndex roleLabels;

    ConfusionMatrix rolesConfusionMatrix;
    ConfusionMatrix framesConfusionMatrix;

    boolean strict;

    public Evaluator( File goldFile, File testFile, File frameLabelsFile, File roleLabelsFile, boolean strict )
            throws IOException {

        this.goldFile = goldFile;
        this.testFile = testFile;
        this.strict = strict;

        frameLabels = InputReader.ReadFeatureIndex( frameLabelsFile, false );
        roleLabels = InputReader.ReadFeatureIndex( roleLabelsFile, false );

        ClassifierResults.FrameLabelList = frameLabels;
        ClassifierResults.RoleLabelList = roleLabels;

        Map<Integer, Sentence> goldSentences = read( goldFile );
        Map<Integer, Sentence> testSentences = read( testFile );

        logger.info( "gold: " + goldFile );
        logger.info( "test: " + testFile );
        logger.debug( "Total sentences: gold = " + goldSentences.size( ) + ", test = " + testSentences.size( ) );

        frameEvaluation = new Evaluation( );
        roleEvaluation = new Evaluation( );

        rolesConfusionMatrix = new ConfusionMatrix( roleLabels.size( ) );
        framesConfusionMatrix = new ConfusionMatrix( frameLabels.size( ) );

        for ( int testId : testSentences.keySet( ) ) {
            logger.info( "============ Evaluating test sentence #" + testId + "... ============" );
            Sentence testSentence = testSentences.get( testId );
            logger.debug( "Test = " + testSentence );
            Sentence goldSentence;
            if ( goldSentences.containsKey( testId ) ) {
                goldSentence = goldSentences.get( testId );
                logger.debug( "Gold = " + goldSentence );
            }
            else {
                logger.warn( "No gold found for test sentence #" + testId + ": " + testSentence + " Skipping ..." );
                continue;
            }
            evaluateFrame( goldSentence, testSentence, frameEvaluation, framesConfusionMatrix );
            evaluateRoles( goldSentence, testSentence, roleEvaluation, rolesConfusionMatrix, strict );
        }

        System.out.println( "gold: " + goldFile.getAbsolutePath( ) );
        System.out.println( "test: " + testFile.getAbsolutePath( ) );

        System.out.println( "Micro averaged statistics" );
        System.out.println( "\ttp\tfp\tfn\ttot\tP\tR\tF1" );
        System.out.println( "frm\t" + frameEvaluation );
        System.out.println( "rol\t" + roleEvaluation );

        System.out.println( "Macro averaged statistics" );
        System.out.println( "\n***  Roles Confusion Matrix  ***" );
        System.out.println( roleLabels );
        System.out.println( rolesConfusionMatrix.toTable( ) );

        System.out.println( "\n***  Frames Confusion Matrix  ***" );
        System.out.println( frameLabels );
        System.out.println( framesConfusionMatrix.toTable( ) );
    }

    void evaluateRoles( Sentence goldSentence, Sentence testSentence, Evaluation roleEvaluation,
                        ConfusionMatrix confusionMatrix, boolean strict ) {

        Set<RoleComparer> goldRoles = new HashSet<>( ),
                testRoles = new HashSet<>( );

        for ( Role r : goldSentence.getAllRoles( ) )
            goldRoles.add( new RoleComparer( r, strict ) );

        for ( Role r : testSentence.getAllRoles( ) )
            testRoles.add( new RoleComparer( r, strict ) );

        Set<RoleComparer> truePositives = new HashSet<>( goldRoles );
        truePositives.retainAll( testRoles );
        for ( RoleComparer tp : truePositives ) {
            roleEvaluation.incTp( );
            confusionMatrix.AddResult( roleLabels.getIndex( tp.role.getName( ) ),
                                       roleLabels.getIndex( tp.role.getName( ) ) );
        }

        Set<RoleComparer> falsePositives = new HashSet<>( testRoles );
        falsePositives.removeAll( goldRoles );
        for ( RoleComparer fp : falsePositives ) {
            roleEvaluation.incFp( );
            confusionMatrix.AddResult( roleLabels.getIndex( fp.role.getName( ) ),
                                       roleLabels.getIndex( "O" ) );
        }

        Set<RoleComparer> falseNegatives = new HashSet<>( goldRoles );
        falseNegatives.removeAll( testRoles );
        for ( RoleComparer fn : falseNegatives ) {
            roleEvaluation.incFn( );
            confusionMatrix.AddResult( roleLabels.getIndex( "O" ),
                                       roleLabels.getIndex( fn.role.getName( ) ) );
        }
    }

    void evaluateFrame( Sentence goldSentence, Sentence testSentence, Evaluation frameEvaluation, ConfusionMatrix confusionMatrix ) {
        logger.info( "----------- Evaluating getFrames... -----------" );
        String goldId = goldSentence.getId( );

        Set<String> test = testSentence.getFrames( );
        Set<String> gold = goldSentence.getFrames( );

        String predictedFrame = test.size( ) == 1 ? test.iterator( ).next( ) : "O";
        String actualFrame = gold.iterator( ).next( );

        confusionMatrix.AddResult( frameLabels.getIndex( predictedFrame ), frameLabels.getIndex( actualFrame ) );

        Iterator<String> goldIterator = gold.iterator( );
        for ( int i = 0; goldIterator.hasNext( ); i++ ) {
            String goldFrame = goldIterator.next( );
            logger.debug( "Gold sentence #" + goldId + ", gold frame [" + goldFrame + "], test getFrames " + test );

            if ( test.contains( goldFrame ) ) {
                frameEvaluation.incTp( );
                logger.warn( "+1 frame TP, total = " + frameEvaluation.getTp( ) );

                confusionMatrix.AddResult( frameLabels.getIndex( goldFrame ), frameLabels.getIndex( goldFrame ) );
            }
            else {
                frameEvaluation.incFn( );
                logger.warn( "+1 frame FN, total = " + frameEvaluation.getTp( ) );
            }
        }

        Iterator<String> testIterator = test.iterator( );
        for ( int i = 0; testIterator.hasNext( ); i++ ) {
            String testFrame = testIterator.next( );
            if ( !gold.contains( testFrame ) ) {
                frameEvaluation.incFp( );
                logger.warn( "+1 frame FP, total = " + frameEvaluation.getTp( ) );
            }
        }
    }

    private Map<Integer, Sentence> read( File fin ) throws IOException {
        LineNumberReader lr = new LineNumberReader( new InputStreamReader( new FileInputStream( fin ), "UTF-8" ) );

        String line = null;
        Map<Integer, Sentence> sentenceMap = new HashMap<>( );
        String sid = null;
        int count = 0;
        Sentence sentence = null;
        while ( ( line = lr.readLine( ) ) != null ) {

            String[] s = line.split( "\t", -1 );
            if ( s.length > 5 ) {

                if ( sid == null ) {
                    sid = s[ 0 ];
                    sentence = new Sentence( sid );
                }
                if ( !s[ 0 ].equalsIgnoreCase( sid ) ) {
                    sentenceMap.put( Integer.parseInt( sid ), sentence );
                    sid = s[ 0 ];
                    sentence = new Sentence( sid );
                }
                if ( !s[ 6 ].trim( ).equalsIgnoreCase( "O" ) ) {
                    ClassifierResults res = ClassifierResults.fromTSV( s, 2 );
                    sentence.add( s[ 0 ], res.getFrame( ), res.getRole( ), res.getToken( ).replace( " ", "" ) );
                }

            }

        }
        sentenceMap.put( Integer.parseInt( sid ), sentence );
        return sentenceMap;
    }

    public void write( File f ) throws IOException {
        PrintWriter pw = new PrintWriter( new BufferedWriter( new OutputStreamWriter( new FileOutputStream( f ), "UTF-8" ) ) );

        pw.println( "gold\t" + goldFile.getName( ) );
        pw.println( "test\t" + testFile.getName( ) + "\n" );
        pw.println( "\ttp\tfp\tfn\ttot\tP\tR\tF1" );
        pw.println( "frm\t" + frameEvaluation );
        pw.println( "rol\t" + roleEvaluation );
        pw.println( "\n*** Roles Confusion Matrix ***" );
        pw.println( rolesConfusionMatrix.toTable( ) );
        pw.println( "\n*** Frames Confusion Matrix ***" );
        pw.println( framesConfusionMatrix.toTable( ) );
        pw.close( );

        File rolesCf = new File( f.getAbsolutePath( ) + ".roles.confusion.csv" );
        pw = new PrintWriter( new BufferedWriter( new OutputStreamWriter( new FileOutputStream( rolesCf ), "UTF-8" ) ) );
        pw.write( rolesConfusionMatrix.toCSV( ClassifierResults.RoleLabelList ) );
        pw.close( );

        File framesCf = new File( f.getAbsolutePath( ) + ".frames.confusion.csv" );
        pw = new PrintWriter( new BufferedWriter( new OutputStreamWriter( new FileOutputStream( framesCf ), "UTF-8" ) ) );
        pw.write( framesConfusionMatrix.toCSV( ClassifierResults.FrameLabelList ) );
        pw.close( );
    }

    public static void main( String[] args ) {
        String logConfig = System.getProperty( "log-config" );
        if ( logConfig == null ) {
            logConfig = "log-config.txt";
        }
        PropertyConfigurator.configure( logConfig );

        Options options = new Options( );
        try {
            Option goldFileOpt = OptionBuilder.withArgName( "file" ).hasArg( ).withDescription( "file from which to read the gold file in tsv format" ).isRequired( ).withLongOpt( "gold" ).create( "g" );
            Option testFileOpt = OptionBuilder.withArgName( "file" ).hasArg( ).withDescription( "file from which to read the test file in tsv format" ).isRequired( ).withLongOpt( "test" ).create( "t" );
            Option roleLabelFileOpt = OptionBuilder.withArgName( "file" ).hasArg( ).withDescription( "file from which to read the gold file in tsv format" ).isRequired( ).withLongOpt( "role-labels" ).create( "r" );
            Option frameLabelFileOpt = OptionBuilder.withArgName( "file" ).hasArg( ).withDescription( "file from which to read the gold file in tsv format" ).isRequired( ).withLongOpt( "frame-labels" ).create( "f" );
            Option strictEvaluation = OptionBuilder.withDescription( "exactly match evaluated FEs" ).withLongOpt("strict-evaluation").create("s");

            options.addOption( "h", "help", false, "print this message" );
            options.addOption( "v", "version", false, "output version information and exit" );

            options.addOption( goldFileOpt );
            options.addOption( testFileOpt );
            options.addOption( roleLabelFileOpt );
            options.addOption( frameLabelFileOpt );
            options.addOption( strictEvaluation );

            CommandLineParser parser = new PosixParser( );
            CommandLine line = parser.parse( options, args );

            File goldFile = new File( line.getOptionValue( "gold" ) );
            File testFile = new File( line.getOptionValue( "test" ) );
            File frameLabels = new File( line.getOptionValue( "frame-labels" ) );
            File roleLabels = new File( line.getOptionValue( "role-labels" ) );
            boolean strict = line.hasOption( "strict-evaluation" );

            Evaluator eval = new Evaluator( goldFile, testFile, frameLabels, roleLabels, strict );
            eval.write( new File( "/tmp/evaluation" ) );
        }
        catch ( ParseException e ) {
            // oops, something went wrong
            System.out.println( "Parsing failed: " + e.getMessage( ) + "\n" );
            HelpFormatter formatter = new HelpFormatter( );
            formatter.printHelp( 400, "java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.Evaluator", "\n", options, "\n", true );
        }
        catch ( IOException e ) {
            logger.error( e );
        }
    }
}