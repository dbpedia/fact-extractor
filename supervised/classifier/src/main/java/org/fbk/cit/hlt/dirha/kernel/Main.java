package org.fbk.cit.hlt.dirha.kernel;

import org.apache.log4j.Logger;

import java.io.*;
import java.util.ArrayList;
import java.util.List;


/**
 * Created with IntelliJ IDEA.
 * User: giuliano
 * Date: 2/1/13
 * Time: 1:42 PM
 * To change this template use File | Settings | File Templates.
 */
public class Main {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>Main</code>.
	 */
	static Logger logger = Logger.getLogger(Main.class.getName());

	/*public List<Sentence> readGoldSentenceList(File f) throws IOException {
		LineNumberReader lnr = new LineNumberReader(new InputStreamReader(new FileInputStream(f), "UTF-8"));
		String line;
		int tot = 0;
		Token token;
		List<Sentence> sentenceList = new ArrayList<Sentence>();
		Sentence sentence = new Sentence();

		while ((line = lnr.readLine()) != null) {

			String[] s = line.split("\t");
			if (s.length == 5) {
				token = new Token(s);
				sentence.addToken(token);
			}
			else {
				sentenceList.addToken(sentence);
				sentence = new Sentence();
			}
		}
		return sentenceList;
	}

	public List<Sentence> readSystemSentenceList(File f) throws IOException {
		List<String> sentenceList = readSystemBlockList(f);
		List<Sentence> sentenceList = new ArrayList<Sentence>();
		for (int i = 0; i < sentenceList.size(); i++) {
			Sentence sentence = new Sentence();;

		}
		return null;
	}

	public Sentence readSentence(String s) throws IOException {
		LineNumberReader lnr = new LineNumberReader(new StringReader(s));
		String[] str = null;
		String line;
		if ((line = lnr.readLine()) != null) {
			str =  line.split(" ");
		}
		Token[] tokens = new Token[str.length];
		for (int i = 0; i < str.length ; i++) {
			 tokens[i] = new Token();
		}
		String[] col;
		while ((line = lnr.readLine()) != null) {
			col =  line.split("\t");

		}
		return null;
	}

	public List<String> readSystemBlockList(File f) throws IOException {
		LineNumberReader lnr = new LineNumberReader(new InputStreamReader(new FileInputStream(f), "UTF-8"));
		String line;
		List<String> sentenceList = new ArrayList<String>();
		StringBuilder sb = new StringBuilder();
		while ((line = lnr.readLine()) != null) {
			if (line.length() > 0) {
				sb.append(line);
			}
			else {
				sb = new StringBuilder();
			}
		}
		return sentenceList;
	}
    */
}
