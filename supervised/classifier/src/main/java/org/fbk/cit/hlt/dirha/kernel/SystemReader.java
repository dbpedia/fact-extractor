package org.fbk.cit.hlt.dirha.kernel;

import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Created with IntelliJ IDEA.
 * User: giuliano
 * Date: 2/4/13
 * Time: 9:54 AM
 * To change this template use File | Settings | File Templates.
 */
public class SystemReader {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>SystemReader</code>.
	 */
	static Logger logger = Logger.getLogger(SystemReader.class.getName());

	List<Sentence> sentenceList;

	public SystemReader(File f) throws IOException {
		sentenceList = new ArrayList<Sentence>();
		read(f);
	}

	public List<Sentence> getSentenceList() {
		return sentenceList;
	}

	void read(File f) throws IOException {
		List<String> blockList = readBlockList(f);

		for (int i = 0; i < blockList.size(); i++) {
			sentenceList.add(readSentence(blockList.get(i)));
		}
	}

	public Sentence readSentence(String s) throws IOException {
		LineNumberReader lnr = new LineNumberReader(new StringReader(s));
		String[] str = null;
		String line;
		Sentence sentence = null;
		if ((line = lnr.readLine()) != null) {
			str =  line.split(" ");

			sentence = new Sentence();
			sentence.addTokens(str);
		}
		while ((line = lnr.readLine()) != null) {
			line = line.trim();
			Pattern framePattern = Pattern.compile("([\\w-]+)\\[\\d+ (\\w+)\\.\\w\\]");
			Matcher frameMatcher = framePattern.matcher(line);
			if (frameMatcher.find())
			{
				String name = frameMatcher.group(1);
				String target = frameMatcher.group(2);
				Frame frame = new Frame(name, target);
				int end = frameMatcher.end(2);
				//logger.debug(end + "\t" + line.substring(end, line.length()));
				Pattern rolePattern = Pattern.compile("([\\w-]+)\\[(\\w[\\w\\d ']*)\\]");
				Matcher roleMatcher = rolePattern.matcher(line.substring(end, line.length()));
				while (roleMatcher.find())
				{
					String n = roleMatcher.group(1);
					String a = roleMatcher.group(2);
					//logger.debug(n + "\t" + a);
					Role role = new Role(n, a);
					frame.addRole(role);
				}

				sentence.addFrame(frame);
			}

		}
		return sentence;
	}

	List<String> readBlockList(File f) throws IOException {
		LineNumberReader lnr = new LineNumberReader(new InputStreamReader(new FileInputStream(f), "UTF-8"));
		String line;
		List<String> list = new ArrayList<String>();
		StringBuilder sb = new StringBuilder();
		while ((line = lnr.readLine()) != null) {
			if (line.length() > 0) {
				sb.append(line);
				sb.append('\n');
			}
			else {

				list.add(sb.toString());
				sb = new StringBuilder();
			}
		}
		return list;
	}

	public static void main(String[] args) throws Exception
	{
		// java com.ml.test.net.HttpServerDemo
		String logConfig = System.getProperty("log-config");
		if (logConfig == null) logConfig = "log-config.txt";

		PropertyConfigurator.configure(logConfig);

		SystemReader systemReader = new SystemReader(new File(args[0]));
		List<Sentence> sentenceList= systemReader.getSentenceList();
		for (int i = 0; i < sentenceList.size(); i++) {
			logger.info(i + "\t" + sentenceList.get(i));
		}
	}
}
