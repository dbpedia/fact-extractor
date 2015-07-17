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
public class FrameFeatureExtraction extends FeatureExtraction {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>FrameFeatureExtraction</code>.
	 */
	static Logger logger = Logger.getLogger(FrameFeatureExtraction.class.getName());

	private FeatureIndex featureIndex;

	private List<String[]> exampleList;

	private Map<String, String> gazetteerMap;

	public String[] columnArray = {"LABEL", "TERM", "LEMMA", "ROLE"};

	public FrameFeatureExtraction(FeatureIndex featureIndex, List<String[]> exampleList, Map<String, String> gazetteerMap) throws IOException {
		this.featureIndex = featureIndex;
		this.exampleList = exampleList;
		this.gazetteerMap = gazetteerMap;
	}

	private Set<Integer> extractColumnFeature(int i, int column) {
		String[] terms = exampleList.get(i)[column].split(" ");
		//String[] roles = exampleList.get(i)[3].split(" ");
		logger.trace(Arrays.toString(terms));
		//logger.debug(Arrays.toString(roles));
		Set<Integer> feat = new HashSet<Integer>();
		for (int j = 0; j < terms.length; j++) {

			//if (terms.length == 4 && terms[3].equalsIgnoreCase("B-LU")) {
			String term = terms[j] + "_" + columnArray[column];

			int k = featureIndex.put(term);

			logger.trace(j + "\t[" + k + "\t" + term + "]");
			if (k != -1) {
				feat.add(k);
			}

			//}

		}
		return feat;
	}

	private Set<Integer> extractRoleFeature(int i) {

		logger.debug(Arrays.toString(exampleList.get(i)));
		String[] terms = exampleList.get(i)[3].trim().split(" ");
		logger.trace(Arrays.toString(terms));
		Set<Integer> feat = new HashSet<Integer>();
		for (int j = 0; j < terms.length; j++) {
			if (!terms[j].equalsIgnoreCase("O")) {
				//String term = terms[j].substring(2, terms[j].length()) + "_" + columnArray[3];
				String term = terms[j] + "_" + columnArray[3];

				//int k = featureIndex.put(term);
				//logger.trace("[" + k + "\t" + term + "]");
				//feat.add(k);

			}

		}
		return feat;
	}

	private Set<Integer> extractGazetteerFeature(int i) {
		String[] terms = exampleList.get(i)[2].split(" ");
		//String[] roles = exampleList.get(i)[3].split(" ");
		logger.trace(Arrays.toString(terms));
		//logger.debug(Arrays.toString(roles));
		Set<Integer> feat = new HashSet<Integer>();
		for (int j = 0; j < terms.length; j++) {
			String category = gazetteerMap.get(terms[j]);
			//logger.debug("category " + category + " (" + exampleList.get(i)[2].toLowerCase() + ")");
			if (category != null) {
				int k = featureIndex.put(category);
				logger.trace(j + "[" + k + "\t" + category + "]");
				if (k != -1) {
					feat.add(k);
				}

			}

		}
		return feat;
	}

	private void add(Set<Integer> feat, SortedSet<Integer> set) {
		/*Iterator<Integer> it = feat.iterator();
		for (int i = 0; i < feat; i++) {
			if (j != -1) {
				set.add(j);
			}

		}*/
		set.addAll(feat);
	}

	public SortedSet<Integer> extract(int i) {
		SortedSet<Integer> set = new TreeSet<Integer>();
		set.addAll(extractColumnFeature(i, 1));
		set.addAll(extractColumnFeature(i, 2));
		set.addAll(extractGazetteerFeature(i));
		//extractRoleFeature(i);
		//set.addAll(extractRoleFeature(i));
		/*add(extractColumnFeature(i, 0), set); //term
		add(extractColumnFeature(i, 1), set); //pos
		add(extractColumnFeature(i, 2), set); //lemma
		add(extractGazetteerFeature(i, 0), set); //gazetteer
     */
		return set;
	}

	public String extractVector(int i) {
		return setToString(extract(i));
	}


}
