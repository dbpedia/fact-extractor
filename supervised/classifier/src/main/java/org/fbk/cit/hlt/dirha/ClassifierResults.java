package org.fbk.cit.hlt.dirha;


public class ClassifierResults implements Token {
    public static FeatureIndex FrameLabelList;
    public static FeatureIndex RoleLabelList;

    public static final String FRAME_NOT_FOUND_LABEL = "FRAME_NOT_FOUND";

    private String token;
    private String pos;
    private String lemma;
    private Double linkConfidence;  // confidence of the linked entity (from the wiki machine)
    private Double roleConfidence;  // confidence of the role (from the svm)
    private Double frameConfidence;
    private int predictedRole;
    private int predictedFrame;
    private String uri;

    public ClassifierResults( String token, String pos, String lemma, Double linkConfidence,
                              Double frameConfidence, Double roleConfidence, int predictedRole,
                              int predictedFrame, String uri ) {
        setToken( token );
        setPos( pos );
        setLemma( lemma );
        setLinkConfidence( linkConfidence );
        setFrameConfidence( frameConfidence );
        setRoleConfidence( roleConfidence );
        setPredictedRole( predictedRole );
        setPredictedFrame( predictedFrame );
        setUri( uri );
    }

    public String getToken( ) {
        return token;
    }

    public String getPos( ) {
        return pos;
    }

    public String getLemma( ) {
        return lemma;
    }

    public Double getLinkConfidence( ) {
        return linkConfidence;
    }

    public String toString( ) {
        return getToken( ) + "\t" + getPos( ) + "\t" + getLemma( );
    }

    public void setToken( String token ) {
        this.token = token;
    }

    public void setPos( String pos ) {
        this.pos = pos;
    }

    public void setLemma( String lemma ) {
        this.lemma = lemma;
    }

    public void setLinkConfidence( Double linkConfidence ) {
        this.linkConfidence = linkConfidence;
    }

    public int getPredictedRole( ) {
        return predictedRole;
    }

    public void setPredictedRole( int predictedRole ) {
        this.predictedRole = predictedRole;
    }

    public int getPredictedFrame( ) {
        return predictedFrame;
    }

    public void setPredictedFrame( int predictedFrame ) {
        this.predictedFrame = predictedFrame;
    }

    public String getPredictedFrameLabel( ) {
        String label = ClassifierResults.FrameLabelList.getTerm( getPredictedFrame( ) );
        if ( label != null )
            return label;
        else return FRAME_NOT_FOUND_LABEL;
    }

    public String getPredictedRoleLabel( ) {
        return ClassifierResults.RoleLabelList.getTerm( getPredictedRole( ) );
    }

    public Double getFrameConfidence( ) {
        return frameConfidence;
    }

    public void setFrameConfidence( Double frameConfidence ) {
        this.frameConfidence = frameConfidence;
    }

    public Double getRoleConfidence( ) {
        return roleConfidence;
    }

    public void setRoleConfidence( Double roleConfidence ) {
        this.roleConfidence = roleConfidence;
    }

    public String getFrame( ) {
        return getPredictedFrameLabel( );
    }

    public String getRole( ) {
        return getPredictedRoleLabel( );
    }

    public void setFrame( String frame ) {
        setPredictedFrame( FrameLabelList.getIndex( frame ) );
    }

    public void setRole( String role ) {
        setPredictedRole( RoleLabelList.getIndex( role ) );
    }

    public String getUri( ) {
        return uri;
    }

    public void setUri( String uri ) {
        this.uri = uri;
    }

    public String toTSV( ) {
        return getToken( ).replace( '_', ' ' ) + "\t" +
                getPos( ).replace( '_', ' ' ) + "\t" +
                getLemma( ).replace( '_', ' ' ) + "\t" +
                getFrame( ) + "\t" +
                getRole( ) + "\t" +
                getFrameConfidence( ) + "\t" +
                getRoleConfidence( ) + "\t" +
                getLinkConfidence( ) + "\t" +
                getUri( );
    }

    public static ClassifierResults fromTSV( String[] parts, int first ) {
        if ( parts.length == 3 + first )
            return new ClassifierResults( parts[ first ], parts[ first + 1 ], parts[ first + 2 ],
                                          0., 0., 0., -1, -1, null );
        else if ( parts.length == 5 + first )
            return new ClassifierResults( parts[ first ], parts[ first + 1 ], parts[ first + 2 ], 0., 0., 0.,
                                          RoleLabelList.getIndex( parts[ first + 4 ] ),
                                          FrameLabelList.getIndex( parts[ first + 3 ] ), "" );
        else if ( parts.length == 9 + first )
            return new ClassifierResults( parts[ first ], parts[ first + 1 ], parts[ first + 2 ],
                                          Double.parseDouble( parts[ first + 7 ] ),
                                          Double.parseDouble( parts[ first + 5 ] ),
                                          Double.parseDouble( parts[ first + 6 ] ),
                                          RoleLabelList.getIndex( parts[ first + 4 ] ),
                                          FrameLabelList.getIndex( parts[ first + 3 ] ),
                                          parts[first + 8]);
        else return null;
    }
}