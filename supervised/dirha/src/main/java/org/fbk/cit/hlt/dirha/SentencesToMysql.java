package org.fbk.cit.hlt.dirha;

import org.annolab.tt4j.TreeTaggerWrapper;
import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;
import org.fbk.cit.hlt.core.analysis.tokenizer.HardTokenizer;
import org.fbk.cit.hlt.core.analysis.tokenizer.Tokenizer;

import java.io.*;

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
 * Time: 10:07 AM
 * To change this template use File | Settings | File Templates.
 */
public class SentencesToMysql {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>SentencesToMysql</code>.
	 */
	static Logger logger = Logger.getLogger(SentencesToMysql.class.getName());

	public SentencesToMysql(File fin, File fout, int start, int size) throws Exception {
		Tokenizer tokenier = new HardTokenizer();
		// Point TT4J to the TreeTagger installation directory. The executable is expected
		// in the "bin" subdirectory - in this example at "/opt/treetagger/bin/tree-tagger"
		System.setProperty("treetagger.home", "/Users/giuliano/Applications/treetagger");
		TreeTaggerWrapper tt = new TreeTaggerWrapper<String>();


		LineNumberReader lr = new LineNumberReader(new InputStreamReader(new FileInputStream(fin), "UTF-8"));
		PrintWriter pw = new PrintWriter(new BufferedWriter(new OutputStreamWriter(new FileOutputStream(fout), "UTF-8")));
		String line = null;

		tt.setModel("/Users/giuliano/Applications/treetagger/lib/italian-utf8.par");
		/*tt.setHandler(new TokenHandler<String>() {
			public void token(String token, String pos, String lemma) {
				System.out.println(token + "\t" + pos + "\t" + lemma);
			}
		});*/
		tt.process(tokenier.stringArray("io sono andato a Roma ieri."));
		int count = 0;
		int end = start + size;
		logger.info("extracting from " + start + " to " + end);
		while ((line = lr.readLine()) != null) {
			if (count >= start && count < end) {
				try {
					TokenWriter tokenWriter = new TokenWriter<String>(pw, count);
					tt.setHandler(tokenWriter);

					//pw.println("sid\ttid\ttoken\tpos\tlemma\tframe\tLU/FE\tnotes\tstart/end time");
					String[] tokens = tokenier.stringArray(line);
					//logger.debug(Arrays.toString(tokens));
					tt.process(tokens);
					pw.print("\n");


				} catch (Exception e) {
					logger.error(e);
				}
			}
			count++;
		}
		pw.close();
		tt.destroy();
	}


	/*class TokenWriter<O> implements TokenHandler<O> {

		private PrintWriter pw;
		private int count;
		private int tc;

		TokenWriter(PrintWriter pw, int count) {
			this.pw = pw;
			this.count = count;
			tc = 0;
		}

		@Override
		public void token(O o, String pos, String lemma) {
			//To change body of implemented methods use File | Settings | File Templates.
			//pw.println(count + "\t" + (++tc) + "\t" + replaceQuote((String) o) + "\t" + pos + "\t" + replaceQuote(lemma) + "\t\tO");
			pw.println(count + "\t" + (++tc) + "\t" + replaceQuote((String) o) + "\t" + pos + "\t" + replaceQuote(lemma) + "\t\t");
		}

		private String replaceQuote(String s) {
			if (s.equals("'")) {
				return "′";
			}
			return s;
		}
	} */

	public static void main(String[] args) throws Exception {
		//java -cp dist/dirha.jar org.fbk.cit.hlt.dirha.SentencesToMysql
		String logConfig = System.getProperty("log-config");
		if (logConfig == null) {
			logConfig = "log-config.txt";
		}
		PropertyConfigurator.configure(logConfig);

		if (args.length != 4) {
			logger.error("java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.SentencesToMysql fin fout start size");
			System.exit(-1);
		}
		File fin = new File(args[0]);
		File fout = new File(args[1]);
		int start = Integer.parseInt(args[2]);
		int size = Integer.parseInt(args[3]);
		new SentencesToMysql(fin, fout, start, size);
	}
}
