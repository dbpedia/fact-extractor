
package org.fbk.cit.hlt.dirha;

import org.apache.log4j.Logger;


import java.io.*;
import java.util.*;

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
 * Date: 10/14/13
 * Time: 11:46 AM
 * To change this template use File | Settings | File Templates.
 */
public class RoleFeatureExtraction extends FeatureExtraction {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>RoleFeatureExtraction</code>.
	 */
	static Logger logger = Logger.getLogger(RoleFeatureExtraction.class.getName());

	private FeatureIndex featureIndex;

	private List<? extends Token> exampleList;

	private Map<String, String> gazetteerMap;

	public String[] columnArray = {"TERM", "POS", "LEMMA"};

	public RoleFeatureExtraction(FeatureIndex featureIndex, List<? extends Token> exampleList,
								 Map<String, String> gazetteerMap) throws IOException {
		this.featureIndex= featureIndex;
		this.exampleList = exampleList;
		this.gazetteerMap = gazetteerMap;
	}

    private int extractColumnFeature( int i, int column, int position ) throws ArrayIndexOutOfBoundsException {
        int k = i + position;
        if ( k < 0 || k >= exampleList.size( ) ) {
            return -1;
        }

		Token example = (Token)exampleList.get( k );
        String feature;
        if ( column == 0 )
            feature = example.getToken( );
        else if ( column == 1 )
            feature = example.getPos( );
        else if ( column == 2 )
            feature = example.getLemma( );
        else throw new ArrayIndexOutOfBoundsException( );

        String term = feature.toLowerCase( ) + "_" + columnArray[ column ] + ( position < 0 ? position : "+" + position );

        int j = featureIndex.put( term );
        logger.trace( "[" + j + "\t" + term + "] " + featureIndex.size( ) );
        return j;
    }

	private int extractGazetteerFeature(int i, int position) throws ArrayIndexOutOfBoundsException {
		int k = i + position;
		if (k < 0 || k >= exampleList.size()) {
			return -1;
		}

		Token example = (Token) exampleList.get(k);
		String category = gazetteerMap.get( example.getLemma( ).toLowerCase( ) );
		if (category == null) {
			return -1;
		}
		String term = category + (position < 0 ? position : "+" + position);

		int j = featureIndex.put(term);
		logger.trace("{" + j + "\t" + term + "} " + featureIndex.size());
		return j;
	}
	
	private void add(int j, SortedSet<Integer> set) {
		if (j != -1) {
			set.add(j);
		}
	}
	public SortedSet<Integer> extract(int i) {
		SortedSet<Integer> set = new TreeSet<Integer>();
				
		//StringBuilder sb = new StringBuilder();
		try {
			add(extractColumnFeature(i, 0, 0), set); //term
			add(extractColumnFeature(i, 0, -1), set); //term -1
			add(extractColumnFeature(i, 0, 1), set); //term +1
			//add(extractColumnFeature(i, 0, -2), set); //term -1
			//add(extractColumnFeature(i, 0, 2), set); //term +1


			add(extractColumnFeature(i, 1, 0), set); //pos
			add(extractColumnFeature(i, 1, -1), set); //pos -1
			add(extractColumnFeature(i, 1, 1), set); //pos +1
			//add(extractColumnFeature(i, 1, -2), set); //pos -1
			//add(extractColumnFeature(i, 1, 2), set); //pos +1


			add(extractColumnFeature(i, 2, 0), set); //lemma
			add(extractColumnFeature(i, 2, -1), set); //lemma -1
			add(extractColumnFeature(i, 2, 1), set); //lemma +1
			//add(extractColumnFeature(i, 2, -2), set); //lemma -1
			//add(extractColumnFeature(i, 2, 2), set); //lemma +1

			add(extractGazetteerFeature(i, 0), set); //gazetteer
			add(extractGazetteerFeature(i, -1), set); //gazetteer -1
			add(extractGazetteerFeature(i, 1), set); //gazetteer +1
			//add(extractGazetteerFeature(i, -2), set); //gazetteer -1
			//add(extractGazetteerFeature(i, 2), set); //gazetteer +1

		} catch (ArrayIndexOutOfBoundsException e) {
			logger.error("error at line " + i + " (" + exampleList.get(i).toString().replace( "\t", "#" ) + ")");
			logger.error(e);
		}

		return set;
	}

	public String extractVector(int i) {
		return setToString(extract(i));
	}
}
