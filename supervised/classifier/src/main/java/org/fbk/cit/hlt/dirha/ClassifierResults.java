package org.fbk.cit.hlt.dirha;


public class ClassifierResults {
    public static FeatureIndex FrameLabelList;
    public static FeatureIndex RoleLabelList;

    public static final String FRAME_NOT_FOUND_LABEL = "O";

    private String token;
    private String pos;
    private String lemma;
    private Double linkConfidence;  // confidence of the linked entity (from the wiki machine)
    private Double roleConfidence;  // confidence of the role (from the svm)
    private Double frameConfidence;
    private int predictedRole;
    private int predictedFrame;

    public ClassifierResults( String token, String pos, String lemma, Double linkConfidence,
                              Double frameConfidence, Double roleConfidence, int predictedRole,
                              int predictedFrame ) {
        setToken( token );
        setPos( pos );
        setLemma( lemma );
        setLinkConfidence( linkConfidence );
        setFrameConfidence( frameConfidence );
        setRoleConfidence( roleConfidence );
        setPredictedRole( predictedRole );
        setPredictedFrame( predictedFrame );
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
}