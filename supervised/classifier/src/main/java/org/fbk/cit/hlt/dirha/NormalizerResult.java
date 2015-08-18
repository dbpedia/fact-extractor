package org.fbk.cit.hlt.dirha;

import org.fbk.cit.hlt.dirha.kernel.StringKernel;

import java.util.HashMap;
import java.util.Map;

public class NormalizerResult {
    public static NormalizerResult FAILURE = new NormalizerResult( false, -1, -1, null, null );

    private int start;
    private int end;
    private boolean success;
    private String category;
    private String normalized;

    public NormalizerResult( Object[] result ) {
        start = ( int ) ( ( Object[] ) result[ 0 ] )[ 0 ];
        end = ( int ) ( ( Object[] ) result[ 0 ] )[ 1 ];
        category = ( String ) result[ 1 ];


        if(result[2] instanceof String)
            normalized = ( String ) result[ 2 ];
        else {
            Map<String, String> obj = (HashMap<String, String>) result[2];
            normalized = obj.get("duration");
        }
        success = ( start >= 0 ) && ( end >= 0 ) && ( category != null ) && ( normalized != null );
    }

    public NormalizerResult( boolean success, int start, int end, String category, String normalized ) {
        this.success = success;
        this.start = start;
        this.end = end;
        this.category = category;
        this.normalized = normalized;
    }

    public int getStart( ) {
        return start;
    }

    public int getEnd( ) {
        return end;
    }

    public boolean isSuccess( ) {
        return success;
    }

    public String getCategory( ) {
        return category;
    }

    public String getNormalized( ) {
        return normalized;
    }

    public String toString( ) {
        return getNormalized( );
    }
}