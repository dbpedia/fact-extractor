package org.fbk.cit.hlt.dirha;


import org.apache.log4j.Logger;

import java.util.*;


public class FrameFeatureExtractor extends FeatureExtraction {
    static Logger logger = Logger.getLogger( FrameFeatureExtractor.class.getName( ) );
    FeatureIndex features;
    Map<String, String> gazetteer;
    String[] columnArray = { "LABEL", "TERM", "LEMMA", "ROLE" };

    public FrameFeatureExtractor( FeatureIndex featureIndex, Map<String, String> gazetteerMap ) {
        this.features = featureIndex;
        this.gazetteer = gazetteerMap;
    }

    public String extractFeatures( List<? extends Token> sentence ) {
        SortedSet<Integer> set = new TreeSet<>( );
        for ( Token t : sentence ) {
            set.addAll( extractColumnFeature( t, 1 ) );
            set.addAll( extractColumnFeature( t, 2 ) );
//            Only add role label features if they are not "O"
            if ( !t.getRole().equalsIgnoreCase("O") )
                set.addAll( extractColumnFeature( t, 3 ) );
            set.addAll( extractGazetteerFeature( t ) );
        }

        return setToString( set );
    }

    Set<Integer> extractColumnFeature( Token t, int column ) {
        String[] terms = null;
        if ( column == 0 )
            terms = t.getFrame( ).split( " " );
        else if ( column == 1 )
            terms = t.getToken( ).split( " " );
        else if ( column == 2 )
            terms = t.getLemma( ).split( " " );
        else if ( column == 3)
            terms = t.getRole( ).split( " " );

        logger.trace( Arrays.toString( terms ) );
        Set<Integer> feat = new HashSet<>( );

        for ( int j = 0; j < terms.length; j++ ) {
            String term = terms[ j ] + "_" + columnArray[ column ];
            int k = features.put( term );

            logger.trace( j + "\t[" + k + "\t" + term + "]" );
            if ( k != -1 )
                feat.add( k );

        }
        return feat;
    }

    Set<Integer> extractGazetteerFeature( Token t ) {
        String[] terms = t.getLemma( ).split( " " );
        logger.trace( Arrays.toString( terms ) );
        Set<Integer> feat = new HashSet<>( );

        for ( int j = 0; j < terms.length; j++ ) {
            String category = gazetteer.get( terms[ j ] );
            if ( category != null ) {
                int k = features.put( category );

                logger.trace( j + "[" + k + "\t" + category + "]" );
                if ( k != -1 )
                    feat.add( k );
            }
        }
        return feat;
    }
}
