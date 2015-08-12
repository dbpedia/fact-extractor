package org.fbk.cit.hlt.dirha;

import net.razorvine.pyro.*;
import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

public class DateNormalizer {
    private static Logger logger = Logger.getLogger( DateNormalizer.class.getName( ) );
    private static PyroProxy proxy;
    private static String uri = "PYRO:date_normalizer@localhost:12937";

    public static NormalizerResult NormalizeOne( String expression ) {
        try {
            Object[] res = ( Object[] ) getProxy( ).call( "normalize_one", expression );
            return new NormalizerResult( res );
        }
        catch ( IOException ex ) {
            logger.error( ex );
            return NormalizerResult.FAILURE;
        }
        catch ( PyroException ex ) {
            logger.error( ex );
            logger.error( ex._pyroTraceback );
            return NormalizerResult.FAILURE;
        }
    }

    public static List<NormalizerResult> NormalizeMany( String expression ) {
        try {
            Object normalized = getProxy( ).call( "normalize_many", expression );
            ArrayList<Object[]> res = ( ArrayList<Object[]> ) normalized;

            ArrayList<NormalizerResult> results = new ArrayList<>( res.size( ) );
            for ( Object[] obj : res )
                results.add( new NormalizerResult( obj ) );
            return results;
        }
        catch ( IOException ex ) {
            logger.error( ex );
            return new ArrayList<>( );
        }
        catch ( PyroException ex ) {
            logger.error( ex );
            logger.error( ex._pyroTraceback );
            return new ArrayList<>( );
        }
    }

    private static PyroProxy getProxy( ) throws IOException {
        if ( proxy == null )
            proxy = new PyroProxy( new PyroURI( uri ) );
        return proxy;
    }

    public static void setUri( String uri ) throws IOException {
        DateNormalizer.uri = uri;
        proxy = null;
        getProxy( );  // better failing now so everybody knows what went wrong
    }

    public static void main( String[] args ) throws IOException {
        BufferedReader in = new BufferedReader( new InputStreamReader( System.in ) );
        String expression;

        initLogger( );

        do {
            System.out.print( "Enter expression to normalize, empty to exit: " );
            expression = in.readLine( );

            if ( expression.length( ) > 0 ) {
                List<NormalizerResult> results = DateNormalizer.NormalizeMany( expression );
                System.out.println( "Normalizer returned " + results.size( ) + "results:" );
                for ( int i = 0; i < results.size( ); i++ ) {
                    System.out.println( "  Result #" + ( i + 1 ) );
                    System.out.println( "    success: " + results.get( i ).isSuccess( ) );
                    System.out.println( "    start: " + results.get( i ).getStart( ) );
                    System.out.println( "    end: " + results.get( i ).getEnd( ) );
                    System.out.println( "    category: " + results.get( i ).getCategory( ) );
                    System.out.println( "    normalized: " + results.get( i ).getNormalized( ) );
                }
            }
        } while ( expression.length( ) > 0 );
    }

    static void initLogger( ) throws IOException {
        String logConfig = System.getProperty( "log-config" );
        Properties defaultProps = new Properties( );
        defaultProps.load( new InputStreamReader( new FileInputStream( logConfig ), "UTF-8" ) );
        PropertyConfigurator.configure( defaultProps );
    }
}
