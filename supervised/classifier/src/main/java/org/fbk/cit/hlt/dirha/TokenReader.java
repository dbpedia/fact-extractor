package org.fbk.cit.hlt.dirha;

import org.annolab.tt4j.TokenHandler;
import org.apache.log4j.Logger;

import java.io.IOException;
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
 * Date: 10/14/13
 * Time: 5:07 PM
 * To change this template use File | Settings | File Templates.
 */
public class TokenReader<O> implements TokenHandler<O> {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>TokenReader</code>.
	 */
	static Logger logger = Logger.getLogger(TokenReader.class.getName());
	private List<String[]> exampleList;
	private int count;
	private int tc;

	TokenReader(List<String[]> exampleList) {
		this.exampleList = exampleList;
	}

	@Override
	public void token(O o, String pos, String lemma) {
		String[] s = new String[3];
		s[0] = replaceQuote((String) o);
		s[1] = pos;
		s[2] = replaceQuote(lemma);
		exampleList.add(s);

	}

	private String replaceQuote(String s) {
		if (s.equals("'")) {
			return "′";
		}
		return s;
	}


}
