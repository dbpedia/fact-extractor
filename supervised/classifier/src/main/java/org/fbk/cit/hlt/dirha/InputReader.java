package org.fbk.cit.hlt.dirha;

import java.io.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

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
        List<List<GenericToken>> list = new ArrayList<>( );
        LineNumberReader lr = new LineNumberReader( new InputStreamReader( new FileInputStream( fin ), "UTF-8" ) );
        String line, sentence_id = null;
        ArrayList<GenericToken> sentence = null;

        while ( ( line = lr.readLine( ) ) != null ) {
            String[] parts = line.split( "\t" );

            if ( sentence_id == null ) {
                sentence_id = parts[ 0 ];
                sentence = new ArrayList<>( );
            }
            else if ( !parts[ 0 ].equals( sentence_id ) ) {
                list.add( sentence );
                sentence_id = parts[ 0 ];
                sentence = new ArrayList<>( );
            }

            sentence.add( new GenericToken( parts[ 2 ], parts[ 3 ], parts[ 4 ], parts[ 5 ], parts[ 6 ] ) );
        }

        return list;
    }

    public static FeatureIndex ReadFeatureIndex(File fin, boolean readonly) throws IOException {
        FeatureIndex labelIndex = new FeatureIndex(readonly);
        labelIndex.read(new InputStreamReader(new FileInputStream(fin), "UTF-8"));
        return labelIndex;
    }
}
