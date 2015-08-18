package org.fbk.cit.hlt.dirha;

import java.io.*;
import java.util.*;

public class InputReader {
    public static Map<String, String> ReadGazetteer( File fin ) throws IOException {
        Map<String, String> map = new HashMap<>( );
        LineNumberReader lr = new LineNumberReader( new InputStreamReader( new FileInputStream( fin ), "UTF-8" ) );

        String line;
        while ( ( line = lr.readLine( ) ) != null ) {
            String[] s = line.split( "\\t+" );
            for ( int i = 1; i < s.length; i++ ) {
                map.put( s[ i ].toLowerCase( ), s[ 0 ].toUpperCase( ) );
            }
        }
        return map;
    }

    public static List<List<GenericToken>> ReadSentences( File fin ) throws IOException {
        LineNumberReader lr = new LineNumberReader( new InputStreamReader( new FileInputStream( fin ), "UTF-8" ) );
        Map<Integer, List<GenericToken>> sentences = new HashMap<>( );
        String line;

        while ( ( line = lr.readLine( ) ) != null ) {
            String[] parts = line.split( "\t" );

            int sentence_id = Integer.parseInt( parts[ 0 ] );
            if ( !sentences.containsKey( sentence_id ) )
                sentences.put( sentence_id, new ArrayList<GenericToken>( ) );

            sentences.get( sentence_id ).add( new GenericToken( parts[ 2 ], parts[ 3 ], parts[ 4 ], parts[ 5 ], parts[ 6 ] ) );
        }

        return new ArrayList<>( sentences.values( ) );
    }

    public static FeatureIndex ReadFeatureIndex( File fin, boolean readonly ) throws IOException {
        FeatureIndex labelIndex = new FeatureIndex( readonly );
        labelIndex.read( new InputStreamReader( new FileInputStream( fin ), "UTF-8" ) );
        return labelIndex;
    }
}
