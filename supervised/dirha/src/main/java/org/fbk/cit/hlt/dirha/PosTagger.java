package org.fbk.cit.hlt.dirha;

import org.annolab.tt4j.TokenHandler;
import org.annolab.tt4j.TreeTaggerWrapper;
import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;
import org.fbk.cit.hlt.core.analysis.tokenizer.HardTokenizer;
import org.fbk.cit.hlt.core.analysis.tokenizer.Tokenizer;


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
 * Date: 10/6/13
 * Time: 5:54 PM
 * To change this template use File | Settings | File Templates.
 */
public class PosTagger {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>PosTagger</code>.
	 */
	static Logger logger = Logger.getLogger(PosTagger.class.getName());


	public static void main(String[] args) {
		String logConfig = System.getProperty("log-config");
		if (logConfig == null) {
			logConfig = "log-config.txt";
		}
		PropertyConfigurator.configure(logConfig);

		//java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.PosTagger

		Tokenizer tokenier = new HardTokenizer();
		TreeTaggerWrapper tt = new TreeTaggerWrapper<String>();
		try {
			if (args[0].equals("it")){
				tt.setModel(System.getProperty("treetagger.home") + "/lib/italian-utf8.par");
			} else if(args[0].equals("en")){
				tt.setModel(System.getProperty("treetagger.home") + "/lib/english.par");
			} else if(args[0].equals("de")){
				tt.setModel(System.getProperty("treetagger.home") + "/lib/german.par");
			}
			tt.setHandler(new TokenHandler<String>() {
				public void token(String token, String pos, String lemma) {
					System.out.println(token + "\t" + pos + "\t" + lemma);
				}
			});
			tt.process(tokenier.stringArray(args[1]));
		} catch (Exception e) {
			logger.error(e);
		} finally {
			tt.destroy();
		}
	}
}
