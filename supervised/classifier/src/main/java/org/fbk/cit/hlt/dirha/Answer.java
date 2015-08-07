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
	private int id;


	List<Entry> list;

	class Entry {
		private int id;
		private String frame;
		private String role;
        private String token;
        private String pos;
        private String lemma;
		private Double roleConfidence;
		private Double frameConfidence;
        private Double linkConfidence;

		Entry(int id, String token, String pos, String lemma, String frame, String role,
              Double roleConfidence, Double frameConfidence, Double linkConfidence ) {

			this.id = id;
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

		int getId() {
			return id;
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
		Sentence sentence = new Sentence(0);
		for (int i = 0; i < list.size(); i++) {
			Entry entry = list.get(i);
			sentence.add(entry.getId(), entry.getFrame(), entry.getRole(), entry.getToken());
		}
		return sentence;
	}

	public Answer(int id, List<ClassifierResults> classifierResultsList ) {
        this.id = id;
        list = new ArrayList<>( );
        logger.debug( "===" );
        logger.debug( classifierResultsList.size( ) );
        String frame = classifierResultsList.get( 0 ).getPredictedRoleLabel( );
        String prevRole = "O";
        for ( int i = 0; i < classifierResultsList.size( ); i++ ) {
            ClassifierResults example = classifierResultsList.get( i );
            String role = example.getPredictedRoleLabel( );

            if ( !example.getToken( ).equalsIgnoreCase( "EOS" ) ) {
                if ( role.equalsIgnoreCase( "O" ) ) {
                    logger.info( i + "\tO\t" + role + "\t" + example.toString( ) + "\t" + example.getLinkConfidence( ) +
                                         "\t" + example.getFrameConfidence( ) );
                    list.add( new Entry( id, example.getToken( ), example.getPos( ), example.getLemma( ),
                                         "O", "O", example.getRoleConfidence( ), example.getFrameConfidence( ),
                                         example.getLinkConfidence( ) ) );
                }
                else {

					logger.info(i + "\t" + frame + "\t" + role + "\t" + example.toString() + "\t");
					if (role.startsWith("I-")) {
						logger.warn(role);
						if (prevRole.startsWith("O")) {
							logger.warn(prevRole);
								//role = "B-" + role.substring(2, role.length());
							role="O";
						}
					}
					else if (role.startsWith("B-")) {
						if (prevRole.startsWith("I-") && sameLabel(prevRole, role)) {
							role = "I-" + role.substring(2, role.length());
						}
					}

                    list.add( new Entry( id, example.getToken( ), example.getPos( ), example.getLemma( ),
                                         frame, role, example.getRoleConfidence( ), example.getFrameConfidence( ),
                                         example.getLinkConfidence( ) ) );
                }

			}
			prevRole = role;
		}
		logger.debug("+++");
	}

	private boolean sameLabel(String r1, String r2) {
		logger.debug(r1 + "\t" + r2);

		String l1 = r1.substring(2, r1.length());
		String l2 = r2.substring(2, r2.length());
		return l1.equals(l2);
	}

	public String toTSV() {
		StringBuilder sb = new StringBuilder();
		for (int i = 0; i < list.size(); i++) {
            Entry entry = list.get( i );
            int id = entry.getId( );
            String frame = entry.getFrame( );
            String role = entry.getRole( );
            sb.append( id );
            sb.append( "\t" );
            sb.append( i + 1 );
            sb.append( "\t" );
            sb.append( entry.getToken( ) );
            sb.append( "\t" );
            sb.append( entry.getPos( ) );
            sb.append( "\t" );
            sb.append( entry.getLemma( ) );
            sb.append( "\t" );
            sb.append( frame );
            sb.append( "\t" );
            sb.append( role );
            sb.append( "\n" );
        }
		sb.append("\n");
		return sb.toString();
	}

    public String confidenceToTSV( ) {
        StringBuilder sb = new StringBuilder( );
        for ( int i = 0; i < list.size( ); i++ ) {
            Entry entry = list.get( i );
            sb.append( entry.getId( ) );
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
        return sb.toString( );
    }

	public String toJSon() {
		StringWriter w = new StringWriter();
		try {


			JsonFactory f = new JsonFactory();
			JsonGenerator g = f.createJsonGenerator(w);
			g.writeStartObject();
			g.writeFieldName("annotation");
			g.writeStartArray();

			for (int i = 0; i < list.size(); i++) {
				Entry entry = list.get(i);
                int id = entry.getId( );
                String frame = entry.getFrame( );
                String role = entry.getRole( );
                g.writeStartObject( );
                g.writeNumberField( "sid", i + 1 );
                g.writeNumberField( "tid", i + 1 );
                g.writeStringField( "token", entry.getToken( ) );
                g.writeStringField( "pos", entry.getPos( ) );
                g.writeStringField( "lemma", entry.getLemma( ) );
                g.writeStringField( "frame", frame );
                g.writeStringField( "role", role );
                g.writeEndObject( );
            }
			g.writeEndArray();
			g.writeEndObject();
			g.close();
		} catch (IOException e) // Because we are writing to a String a
		{
			logger.error(e);
		}
		return w.toString();


	}


	public String toHtml() {

		StringBuilder sb = new StringBuilder();
		String prevRole = "o";
		String prevFrame = "o";
		String currentRole = null;
		String currentFrame = null;
		String sentenceFrame = null;
		for (int i = 0; i < list.size(); i++) {
			Entry entry = list.get(i);

			currentRole = entry.getRole();
			currentFrame = entry.getFrame();
			if (!currentFrame.equalsIgnoreCase("o")) {
				sentenceFrame = currentFrame;
			}

			logger.debug(i + "\t" + currentRole + "\t"+ currentFrame);
			if (currentRole.startsWith("B-")) {
				//logger.debug("a\t\t" + role);
				if (!prevRole.equalsIgnoreCase("o")) {
					sb.append("]");
					sb.append("<sub>");
					sb.append(prevRole.substring(2, prevRole.length()));
					sb.append("</sub>");

				}
				if (i > 0) {
					sb.append(" ");
				}

				sb.append("[");
				//sb.append(entry.getExample()[0]);
			}


			else if (currentRole.equalsIgnoreCase("o") && !prevRole.equalsIgnoreCase("o")) {
				sb.append("]");
				sb.append("<sub>");
				sb.append(prevRole.substring(2, prevRole.length()));
				sb.append("</sub>");
				if (i > 0) {
					sb.append(" ");
				}
				//sb.append(entry.getExample()[0]);
			}
			else {
				if (i > 0) {
					sb.append(" ");
				}
			}

			sb.append(StringEscapeUtils.escapeHtml(entry.getToken()));

			prevRole = currentRole;
			prevFrame = currentFrame;
		}

		if ((prevRole.startsWith("B-") || prevRole.startsWith("I-"))) {
			sb.append("]");
			sb.append("<sub>");
			sb.append(prevRole.substring(2, prevRole.length()));
			sb.append("</sub>");
		}

		//logger.debug("after\t" + list);
		return sentenceFrame + ": " + sb.toString();
	}


}

