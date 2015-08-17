package org.fbk.cit.hlt.dirha;

import java.util.Formatter;

public class ConfusionMatrix {
    private class AverageCalculator {
        double sum = 0.;
        int count = 0;

        public void addMeasure( double measure ) {
            if ( !Double.isNaN( measure ) ) {
                sum += measure;
                count += 1;
            }
        }

        double getAverage( ) {
            return sum / count;
        }
    }

    private int[][] matrix;
    private int size;

    public ConfusionMatrix( int size ) {
        this.size = size;

        matrix = new int[ size ][];
        for ( int i = 0; i < size; i++ ) {
            matrix[ i ] = new int[ size ];
            for ( int j = 0; j < size; j++ )
                matrix[ i ][ j ] = 0;
        }
    }

    public int AddResult( int predicted, int actual ) {
        matrix[ predicted ][ actual ] += 1;
        return matrix[ predicted ][ actual ];
    }

    public float getPrecision( int label ) {
        int sum = 0;
        for ( int i = 0; i < size; i++ )
            sum += matrix[ label ][ i ];
        return ( ( float ) matrix[ label ][ label ] ) / sum;
    }

    public float getRecall( int label ) {
        int sum = 0;
        for ( int i = 0; i < size; i++ )
            sum += matrix[ i ][ label ];
        return ( ( float ) matrix[ label ][ label ] ) / sum;
    }

    public String toTable( ) {
        StringBuilder sb = new StringBuilder( );
        int columnSum[] = new int[ size ];
        AverageCalculator precisionAverage = new AverageCalculator( ),
                recallAverage = new AverageCalculator( ),
                f1Average = new AverageCalculator( );

        sb.append( " actual --> | " );
        for ( int i = 0; i < size; i++ ) {
            sb.append( new Formatter( ).format( "%5d |", i ) );
            columnSum[ i ] = 0;
        }
        sb.append( "  count | precision | recall |    f1 |\n" );

        for ( int i = 0; i < size; i++ ) {
            int rowSum = 0;
            sb.append( new Formatter( ).format( "%12d| ", i ) );

            for ( int j = 0; j < size; j++ ) {
                sb.append( new Formatter( ).format( "%5d |", matrix[ i ][ j ] ) );
                rowSum += matrix[ i ][ j ];
                columnSum[ j ] += matrix[ i ][ j ];
            }

            double precision = getPrecision( i ),
                    recall = getRecall( i ),
                    f1 = 2 * ( precision * recall ) / ( precision + recall );

            precisionAverage.addMeasure( precision );
            recallAverage.addMeasure( recall );
            f1Average.addMeasure( f1 );

            sb.append( new Formatter( ).format( "%7d |%10.2f |%7.2f |%6.2f |\n",
                                                rowSum, precision, recall, f1 ) );
        }

        sb.append( "      count | " );
        for ( int i = 0; i < size; i++ )
            sb.append( new Formatter( ).format( "%5d |", columnSum[ i ] ) );

        sb.append( new Formatter( ).format( " avg -->|%10.2f |%7.2f |%6.2f |\n",
                                            precisionAverage.getAverage( ),
                                            recallAverage.getAverage( ),
                                            f1Average.getAverage( ) ) );

        sb.append( "\n" );
        return sb.toString( );
    }

    public String toCSV( FeatureIndex labels ) {
        StringBuilder sb = new StringBuilder( );
        int columnSum[] = new int[ size ];
        AverageCalculator precisionAverage = new AverageCalculator( ),
                recallAverage = new AverageCalculator( ),
                f1Average = new AverageCalculator( );

        sb.append( "actual -->;" );
        for ( int i = 0; i < size; i++ ) {
            columnSum[ i ] = 0;
            sb.append( labels.getTerm( i ) );
            sb.append( ";" );
        }
        sb.append( "count;precision;recall;f1\n" );

        for ( int i = 0; i < size; i++ ) {
            int rowSum = 0;
            sb.append( labels.getTerm( i ) );
            sb.append( ";" );

            for ( int j = 0; j < size; j++ ) {
                sb.append( matrix[ i ][ j ] );
                sb.append( ";" );

                rowSum += matrix[ i ][ j ];
                columnSum[ j ] += matrix[ i ][ j ];
            }

            double precision = getPrecision( i ),
                    recall = getRecall( i ),
                    f1 = 2 * ( precision * recall ) / ( precision + recall );

            precisionAverage.addMeasure( precision );
            recallAverage.addMeasure( recall );
            f1Average.addMeasure( f1 );

            sb.append( rowSum );
            sb.append( ";" );
            sb.append( precision );
            sb.append( ";" );
            sb.append( recall );
            sb.append( ";" );
            sb.append( f1 );
            sb.append( "\n" );
        }

        sb.append( "count;" );
        for ( int i = 0; i < size; i++ ) {
            sb.append( columnSum[ i ] );
            sb.append( ";" );
        }

        sb.append( ";" );
        sb.append( precisionAverage.getAverage( ) );
        sb.append( ";" );
        sb.append( recallAverage.getAverage( ) );
        sb.append( ";" );
        sb.append( f1Average.getAverage( ) );
        sb.append( "\n" );

        sb.append( "\n" );
        return sb.toString( );
    }
}
