package org.fbk.cit.hlt.dirha;

import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;

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
 * Date: 10/4/13
 * Time: 5:06 PM
 * To change this template use File | Settings | File Templates.
 */
public class Prova {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>Prova</code>.
	 */
	static Logger logger = Logger.getLogger(Prova.class.getName());

	public static void main(String[] args) throws Exception {
		//java -cp dist/dirha.jar org.fbk.cit.hlt.dirha.Prova
		String logConfig = System.getProperty("log-config");
		if (logConfig == null) {
			logConfig = "log-config.txt";
		}

		PropertyConfigurator.configure(logConfig);

		LineNumberReader lr = new LineNumberReader(new InputStreamReader(new FileInputStream(args[0]), "UTF-8"));
		PrintWriter pw = new PrintWriter(new BufferedWriter(new OutputStreamWriter(new FileOutputStream(args[1]), "UTF-8")));
		String line = null;

		while ((line = lr.readLine()) != null) {
			String[] s = line.split("\t");
			if (s.length == 1) {
				pw.println(s[0]);
			}
			/*else if (s.length == 2) {
				pw.print(s[0]);
				pw.print(" ");
				pw.println(s[1]);
			}  */
			else {
				for (int i = 1; i < s.length; i++) {
					pw.print(s[0]);
					pw.print(" ");
					pw.println(s[i]);

				}

			}


		}
		pw.close();
	}
}
