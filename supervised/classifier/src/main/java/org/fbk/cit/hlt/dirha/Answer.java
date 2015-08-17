package org.fbk.cit.hlt.dirha;

import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonGenerator;
import org.apache.commons.lang.StringEscapeUtils;
import org.apache.log4j.Logger;

import java.io.IOException;
import java.io.StringWriter;
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


	List<Entry> list;

    public String getSentenceID( ) {
        return sentenceID;
    }

    public void setSentenceID( String sentenceID ) {
        this.sentenceID = sentenceID;
    }

    class Entry {
		private String frame;
		private String role;
        private String token;
        private String pos;
        private String lemma;
		private Double roleConfidence;
		private Double frameConfidence;
        private Double linkConfidence;

		Entry(String token, String pos, String lemma, String frame, String role,
              Double roleConfidence, Double frameConfidence, Double linkConfidence ) {

			this.frame = frame;
			this.role = role;
			this.token = token;
            this.pos = pos;
            this.lemma = lemma;
            this.roleConfidence = roleConfidence;
            this.frameConfidence = frameConfidence;
            this.linkConfidence = linkConfidence;
		}

		String getFrame() {
			return frame;
		}

		String getRole() {
			return role;
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

        public Double getRoleConfidence( ) {
            return roleConfidence;
        }

        public Double getFrameConfidence( ) {
            return frameConfidence;
        }

        public Double getLinkConfidence( ) {
            return linkConfidence;
        }
    }

	public Sentence getSentence() {
		Sentence sentence = new Sentence(sentenceID);
		for (int i = 0; i < list.size(); i++) {
			Entry entry = list.get(i);
			sentence.add( getSentenceID( ), entry.getFrame(), entry.getRole(), entry.getToken());
		}
		return sentence;
	}

	public Answer(String sentenceID, List<ClassifierResults> classifierResultsList ) {
        this.setSentenceID( sentenceID );
        list = new ArrayList<>( );
        logger.debug( "===" );
        logger.debug( classifierResultsList.size( ) );

        for(ClassifierResults example: classifierResultsList) {
            if ( !example.getToken( ).equalsIgnoreCase( "EOS" ) ) {
                    list.add( new Entry( example.getToken( ), example.getPos( ), example.getLemma( ),
                                         example.getPredictedFrameLabel(), example.getPredictedRoleLabel(),
                                         example.getRoleConfidence( ), example.getFrameConfidence( ),
                                         example.getLinkConfidence( ) ) );
			}
		}
	}

	public String toTSV() {
		StringBuilder sb = new StringBuilder();
		for (int i = 0; i < list.size(); i++) {
            Entry entry = list.get( i );
            sb.append( getSentenceID( ) );
            sb.append( "\t" );
            sb.append( i + 1 );
            sb.append( "\t" );
            sb.append( entry.getToken( ).replace( '_', ' ' ) );
            sb.append( "\t" );
            sb.append( entry.getPos( ).replace( '_', ' ' ) );
            sb.append( "\t" );
            sb.append( entry.getLemma( ).replace( '_', ' ' ) );
            sb.append( "\t" );
            sb.append( entry.getFrame( ) );
            sb.append( "\t" );
            sb.append( entry.getRole( ) );
            sb.append( "\n" );
        }
		sb.append("\n");
		return sb.toString();
	}

    public String confidenceToTSV( ) {
        StringBuilder sb = new StringBuilder( );
        for ( int i = 0; i < list.size( ); i++ ) {
            Entry entry = list.get( i );
            sb.append( getSentenceID( ) );
            sb.append( "\t" );
            sb.append( i + 1 );
            sb.append( "\t" );
            sb.append( entry.getFrameConfidence( ) );
            sb.append( "\t" );
            sb.append( entry.getRoleConfidence( ) );
            sb.append( "\t" );
            sb.append( entry.getLinkConfidence( ) );
            sb.append( "\n" );
        }
        sb.append("\n");
        return sb.toString( );
    }
}

