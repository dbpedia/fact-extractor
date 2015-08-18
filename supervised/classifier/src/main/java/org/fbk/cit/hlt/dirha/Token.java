package org.fbk.cit.hlt.dirha;


public interface Token {
    String getToken( );

    String getPos( );

    String getLemma( );

    String getFrame( );

    String getRole( );

    void setToken( String token );

    void setPos( String pos );

    void setLemma( String lemma );

    void setFrame( String frame );

    void setRole( String role );
}