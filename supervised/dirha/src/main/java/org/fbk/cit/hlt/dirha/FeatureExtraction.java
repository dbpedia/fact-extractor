package org.fbk.cit.hlt.dirha;

import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;

import java.util.Iterator;
import java.util.SortedSet;

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
 * Date: 11/6/13
 * Time: 3:22 PM
 * To change this template use File | Settings | File Templates.
 */
public abstract class FeatureExtraction {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>FeatureExtraction</code>.
	 */
	static Logger logger = Logger.getLogger(FeatureExtraction.class.getName());

	protected String setToString(SortedSet<Integer> set) {
		StringBuilder sb = new StringBuilder();
		Iterator<Integer> it = set.iterator();
		for (int i = 0; it.hasNext(); i++) {
			if (i > 0) {
				sb.append(" ");
			}
			int j = it.next();
			sb.append(j);
			sb.append(":1");
		}
		return sb.toString();
	}
}
