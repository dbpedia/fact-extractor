package org.fbk.cit.hlt.dirha;


public class GenericToken implements Token {
    private String token;
    private String pos;
    private String lemma;
    private String frame;
    private String role;

    public GenericToken( String token, String pos, String lemma, String frame, String role ) {
        setToken( token );
        setPos( pos );
        setLemma( lemma );
        setFrame( frame );
        setRole( role );
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

    public String getRole( ) {
        return role;
    }

    public void setRole( String role ) {
        this.role = role;
    }

    public String toString( ) {
        return getToken( ) + "\t" + getPos( ) + "\t" + getLemma( ) + "\t"
                + getFrame( ) + "\t" + getRole( );
    }
}
