package org.fbk.cit.hlt.dirha;

import org.apache.log4j.Logger;
import java.util.ArrayList;
import java.util.List;

/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

/**
 * Created with IntelliJ IDEA.
 * User: giuliano
 * Date: 11/25/13
 * Time: 12:20 PM
 * To change this template use File | Settings | File Templates.
 */
public class Answer {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>Answer</code>.
	 */
	static Logger logger = Logger.getLogger(Answer.class.getName());
	private String sentenceID;

	List<ClassifierResults> list;

    public String getSentenceID( ) {
        return sentenceID;
    }

    public void setSentenceID( String sentenceID ) {
        this.sentenceID = sentenceID;
    }

	public Sentence getSentence() {
		Sentence sentence = new Sentence(sentenceID);
        for(ClassifierResults entry: list)
			sentence.add( getSentenceID( ), entry.getFrame(), entry.getRole(), entry.getToken());
		return sentence;
	}

	public Answer(String sentenceID, List<ClassifierResults> classifierResultsList ) {
        this.setSentenceID( sentenceID );
        list = new ArrayList<>( );
        logger.debug( "===" );
        logger.debug( classifierResultsList.size( ) );

        for(ClassifierResults example: classifierResultsList) {
            if ( !example.getToken( ).equalsIgnoreCase( "EOS" ) )
                list.add( example );
		}
	}

    public String toTSV( ) {
        StringBuilder sb = new StringBuilder( );
        for ( int i = 0; i < list.size( ); i++ ) {
            ClassifierResults entry = list.get( i );
            sb.append( getSentenceID( ) );
            sb.append( "\t" );
            sb.append( i + 1 );
            sb.append( "\t" );
            sb.append( entry.toTSV( ) );
            sb.append( "\n" );
        }
        sb.append( "\n" );
        return sb.toString( );
    }
}

