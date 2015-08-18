package org.fbk.cit.hlt.dirha;


import org.apache.log4j.Logger;

import java.io.IOException;
import java.util.*;

public class RoleFeatureExtractor extends FeatureExtraction {
    static Logger logger = Logger.getLogger( RoleFeatureExtractor.class.getName( ) );
    private FeatureIndex featureIndex;
    private Map<String, String> gazetteer;

    public RoleFeatureExtractor( FeatureIndex featureIndex, Map<String, String> gazetteerMap ) throws IOException {
        this.featureIndex = featureIndex;
        this.gazetteer = gazetteerMap;
    }

    public String extractFeatures( List<? extends Token> sentence, int tokenPosition ) {
        SortedSet<Integer> set = new TreeSet<>( );

        int m = 2;  // extract features for +/- m tokens around tokenPosition
        for ( int i = Math.max( tokenPosition - m, 0 ),
              max = Math.min( tokenPosition + m + 1, sentence.size( ) );
              i < max; i++ ) {

            int rel = i - tokenPosition;
            check_add( set, featureFor( sentence.get( i ).getToken( ), "TERM", rel ) );
            check_add( set, featureFor( sentence.get( i ).getPos( ), "POS", rel ) );
            check_add( set, featureFor( sentence.get( i ).getLemma( ), "LEMMA", rel ) );
            check_add( set, gazeetteerFeatureFor( sentence.get( i ).getLemma( ), rel ) );
        }

        return setToString( set );
    }

    private void check_add( Set<Integer> set, int feature ) {
        if ( feature >= 0 ) set.add( feature );
    }

    private int featureFor( String term, String type, int position ) {
        String feature = term.toLowerCase( ).replace( ' ', '_' ) + "_" + type + ( position < 0 ? position : "+" + position );
        return featureIndex.put( feature );
    }

    private int gazeetteerFeatureFor( String lemma, int position ) {
        String category = gazetteer.get( lemma.toLowerCase( ) );
        if ( category != null ) {
            String term = category + ( position < 0 ? position : "+" + position );
            return featureIndex.put( term );
        }
        else return -1;
    }
}
