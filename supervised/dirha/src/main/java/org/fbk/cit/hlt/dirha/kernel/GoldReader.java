package org.fbk.cit.hlt.dirha.kernel;

import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;

import java.io.*;
import java.util.ArrayList;
import java.util.List;

/**
 * Created with IntelliJ IDEA.
 * User: giuliano
 * Date: 2/1/13
 * Time: 2:18 PM
 * To change this template use File | Settings | File Templates.
 */
public class GoldReader {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>GoldReader</code>.
	 */
	static Logger logger = Logger.getLogger(GoldReader.class.getName());

	List<Sentence> sentenceList;

	public GoldReader(File f) throws IOException {
		sentenceList = new ArrayList<Sentence>();
		read(f);
	}

	public List<Sentence> getSentenceList() {
		return sentenceList;
	}

	void read(File f) throws IOException {
		LineNumberReader lnr = new LineNumberReader(new InputStreamReader(new FileInputStream(f), "UTF-8"));
		String line;
		int tot = 0, sent = 0;
		Token token;
		Sentence sentence = new Sentence();
		Frame frame = null;
		String currentRole = "-";
		StringBuilder argBuilder = new StringBuilder();
		List<Role> roleList = new ArrayList<Role>();
		while ((line = lnr.readLine()) != null) {

			String[] s = line.split("\t");
			if (s.length == 5) {
				//logger.debug(line);
				sentence.addToken(s[1]);
				if (s[4].equalsIgnoreCase("target"))
				{
					frame = new Frame(s[3], s[1]);
				}

				//logger.debug(s[0] + "\t" + s[4] + "\t" + currentRole);
				if (!s[4].equalsIgnoreCase(currentRole))
				{
					if (!currentRole.equals("-") && !currentRole.equalsIgnoreCase("target"))
					{
						Role role = new Role(currentRole, argBuilder.toString());
						roleList.add(role);
					}
					currentRole = s[4];
					argBuilder = new StringBuilder();
					argBuilder.append(s[1]);
				}
				else
				{
					argBuilder.append(" ");
					argBuilder.append(s[1]);
				}
				//currentRole = s[4];
				tot++;
			}
			else {

				frame.setRoleList(roleList);
				sentence.addFrame(frame);
				sentenceList.add(sentence);
				roleList = new ArrayList<Role>();
				sentence = new Sentence();
				sent++;
			}
		}
	}

	public static void main(String[] args) throws Exception
	{
		// java com.ml.test.net.HttpServerDemo
		String logConfig = System.getProperty("log-config");
		if (logConfig == null) logConfig = "log-config.txt";

		PropertyConfigurator.configure(logConfig);

		GoldReader goldReader = new GoldReader(new File(args[0]));
		List<Sentence> sentenceList= goldReader.getSentenceList();
		for (int i = 0; i < sentenceList.size(); i++) {
			 logger.info(i + "\t" + sentenceList.get(i));
		}
	}
}
