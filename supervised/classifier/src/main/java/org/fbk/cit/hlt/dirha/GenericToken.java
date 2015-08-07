package org.fbk.cit.hlt.dirha;


public class GenericToken implements Token {
    private String token;
    private String pos;
    private String lemma;
    private String frame;
    private String tag;

    public GenericToken( String token, String pos, String lemma, String frame, String tag ) {
        setToken( token );
        setPos( pos );
        setLemma( lemma );
        setFrame( frame );
        setTag( tag );
    }

    @Override
    public String getToken( ) {
        return token;
    }

    public void setToken( String token ) {
        this.token = token;
    }

    @Override
    public String getPos( ) {
        return pos;
    }

    public void setPos( String pos ) {
        this.pos = pos;
    }

    @Override
    public String getLemma( ) {
        return lemma;
    }

    public void setLemma( String lemma ) {
        this.lemma = lemma;
    }

    public String getFrame( ) {
        return frame;
    }

    public void setFrame( String frame ) {
        this.frame = frame;
    }

    public String getTag( ) {
        return tag;
    }

    public void setTag( String tag ) {
        this.tag = tag;
    }

    public String toString( ) {
        return getToken( ) + "\t" + getPos( ) + "\t" + getLemma( ) + "\t"
                + getFrame( ) + "\t" + getTag( );
    }
}
