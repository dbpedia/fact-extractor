package org.fbk.cit.hlt.dirha;

import org.apache.commons.cli.*;
import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;
import org.fbk.cit.hlt.core.analysis.tokenizer.HardTokenizer;
import org.fbk.cit.hlt.core.analysis.tokenizer.Tokenizer;
import org.fbk.cit.hlt.dirha.kernel.CharKernel;

import java.io.*;
import java.util.*;

/**
 * Created with IntelliJ IDEA.
 * User: giuliano
 * Date: 9/4/14
 * Time: 12:01 PM
 * To change this template use File | Settings | File Templates.
 * <p/>
 * This class takes as input the annotation reference in Italian, the phrase table (it-term \t other-lang-term),
 * the translated sentences (in the annotation reference format using TranslatedSentencesToSpreadSheet) and
 * returns the training set in the other language.
 *
 * @see SpreadSheetToSentencesToBeTranslated
 * @see TranslatedSentencesToSpreadSheet
 */
public class AnnotationMigration {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>AnnotationMigration</code>.
	 */
	static Logger logger = Logger.getLogger(AnnotationMigration.class.getName());

	Map<String, String[]> roleMap;
	Tokenizer tokenier;
	PrintWriter pw;

	public AnnotationMigration(File labelled, File unlabelled, File roles, File output) throws IOException {
		this(labelled, unlabelled, roles, output, 0);
	}
	public AnnotationMigration(File labelled, File unlabelled, File roles, File output, int start) throws IOException {
		pw = new PrintWriter(new BufferedWriter(new OutputStreamWriter(new FileOutputStream(output), "UTF-8")));
		tokenier = new HardTokenizer();
		Map<Integer, String> labelledMap = readTraining(labelled);
		Map<Integer, String> unlabelledMap = readTraining(unlabelled);
		roleMap = readRoles(roles);
		//logger.info(labelledMap);
		if (labelledMap.size() != unlabelledMap.size()) {
			logger.warn(labelledMap.size() + " != " + unlabelledMap.size());
		}

		for (int i = start; i < labelledMap.size(); i++) {
			logger.info(i);

			logger.info("\n" + labelledMap.get(i));
			logger.info("\n" + unlabelledMap.get(i));

			process(labelledMap.get(i), unlabelledMap.get(i));
			logger.info("***\n");
		}

		/*Iterator<Integer> it = unlabelledMap.keySet().iterator();
		while(it.hasNext()) {
			int id = it.next();
			if (labelledMap.get(id)==null){
				logger.warn(id);
				logger.warn(unlabelledMap.get(id));

			}
		}*/
		pw.close();
	}

	private String replace(String s) {
		return s.replaceAll("′", "'").replaceAll("po'", "po");
	}


	private List<String> extractRoles(String t) throws IOException {
		///logger.debug("\n" + t);
		List<String> list = new ArrayList<String>();
		LineNumberReader lr = new LineNumberReader(new StringReader(t));
		String line = null;

		String role = null;
		String annotation = null;
		while ((line = lr.readLine()) != null) {
			String[] s = line.split("\t");
			if (s[6].toLowerCase().startsWith("b-")) {
				logger.debug("a\t\t" + role);

				if (role != null && annotation != null) {

					list.add(role + "\t" + annotation);
					logger.warn("adding " + role + "\t" + annotation);
				}
				role = new String(s[2]);
				annotation = s[5] + "\t" + s[6];
			}
			else if (s[6].toLowerCase().startsWith("i-")) {
				if (role != null) {
					role += " " + s[2];
				}
			}
		}
		if (role != null && annotation != null) {
			list.add(role + "\t" + annotation);
			logger.warn("adding " + role + "\t" + annotation);
		}
		return list;
	}

	private List<String[]> extractExamples(String t) throws IOException {
		//logger.debug("\n" + t);
		List<String[]> list = new ArrayList<String[]>();
		LineNumberReader lr = new LineNumberReader(new StringReader(t));
		String line = null;

		String role = null;
		String annotation = null;
		while ((line = lr.readLine()) != null) {
			String[] s = line.split("\t");
			list.add(s);
		}
		return list;
	}


	private void process(String labelled, String unlabelled) throws IOException {
		if (labelled == null || unlabelled == null) {
			return;
		}
		List<String[]> examples = extractExamples(unlabelled);
		List<String> roles = extractRoles(labelled);
		boolean[] found = new boolean[roles.size()];

		logger.debug("roles: " + roles);
		for (int i = 0; i < roles.size(); i++) {

			String[] t = roles.get(i).split("\t");
			String[] translatedRole = roleMap.get(t[0]);
			if (translatedRole != null) {
				for (int k = 2; k < translatedRole.length; k++) {
					logger.debug(i + "\t" + roles.get(i) + "\t" + translatedRole[k]);
					if (translatedRole[k] != null) {
						Boundary boundary = matcher(translatedRole[k], examples);
						if (boundary != null) {
							logger.info("///");
							logger.debug(boundary + "\t" + translatedRole[k] + ":");
							logger.debug(boundary.begin + "\t" + Arrays.toString(examples.get(boundary.begin)));
							examples.get(boundary.begin)[5] = t[1];
							examples.get(boundary.begin)[6] = t[2];
							for (int j = boundary.begin + 1; j <= boundary.end; j++) {
								logger.debug(j + "\t" + Arrays.toString(examples.get(j)));
								examples.get(j)[5] = t[1];
								examples.get(j)[6] = t[2].replaceAll("B-", "I-");
							}
							found[i] = true;
							logger.info("\\\\\\ break at " + k + "/" + translatedRole.length);
							break;
						}

					}
				}
			}
		}

		logger.info("===");
		boolean b=false;
		for (int i = 0; i < found.length; i++) {
			if (!found[i]) {
				String[] t = roles.get(i).split("\t");
				logger.info("# Missing " + t[0] + "\t" +t[1] + "\t" + t[2]);

				pw.println("# Missing " + t[0] + "\t" +t[1] + "\t" + t[2]);
				b = true;
			}
		}
		if (b){
			StringBuilder sb = new StringBuilder();
			for (int j = 0; j < examples.size(); j++) {
				if (j >0)   {
					sb.append(" ");
				}
				sb.append(examples.get(j)[2]);
			}
			logger.info("# " + sb.toString());
		}


		for (int i = 0; i < examples.size(); i++) {
			String[] example = examples.get(i);
			logger.info(example[0] + "\t" + example[1] + "\t" + example[2] + "\t" + example[3] + "\t" + example[4] + "\t" + example[5] + "\t" + example[6]);
			pw.println(example[0] + "\t" + example[1] + "\t" + example[2] + "\t" + example[3] + "\t" + example[4] + "\t" + example[5] + "\t" + example[6]);

		}
		pw.print("\n");
		logger.info("***");
	}

	private Map<String, String[]> readRoles(File f) throws IOException {
		Map<String, String[]> map = new TreeMap<String, String[]>();

		LineNumberReader lr = new LineNumberReader(new InputStreamReader(new FileInputStream(f), "UTF-8"));
		String line = null;
		StringBuilder sb = new StringBuilder();

		while ((line = lr.readLine()) != null) {
			String[] s = line.toLowerCase().split("\t");
			if (s.length > 2) {
				logger.trace(Arrays.toString(s));
				map.put(s[1], s);
			}
		}

		return map;
	}

	private class Boundary {
		int begin;
		int end;

		Boundary(int begin, int end) {
			this.begin = begin;
			this.end = end;
		}

		int getBegin() {
			return begin;
		}

		int getEnd() {
			return end;
		}

		@Override
		public String toString() {
			return
					begin + ", " + end;
		}
	}

	private Boundary matcher(String role, List<String[]> sentence) {

		String[] t = tokenier.stringArray(role);
		logger.debug(Arrays.toString(t));


		return ngramMatcher(t, sentence, t.length);


		/*if (t.length == 2) {
			for (int i = 0; i < sentence.size() - 1; i++) {
				if (t[0].equals(sentence.get(i)[2]) && t[1].equals(sentence.get(i + 1)[2])) {
					return new Boundary(i, i + 1);
				}
			}
		}
		else if (t.length == 3) {
			for (int i = 0; i < sentence.size() - 2; i++) {
				if (t[0].equals(sentence.get(i)[2]) && t[1].equals(sentence.get(i + 1)[2]) && t[2].equals(sentence.get(i + 2)[2])) {
					return new Boundary(i, i + 2);
				}
			}
		}
		else if (t.length == 4) {
			for (int i = 0; i < sentence.size() - 3; i++) {
				if (t[0].equals(sentence.get(i)[2]) && t[1].equals(sentence.get(i + 1)[2]) && t[2].equals(sentence.get(i + 2)[2]) && t[3].equals(sentence.get(i + 3)[2])) {
					return new Boundary(i, i + 3);
				}
			}
		}
		else if (t.length == 1) {
			for (int i = 0; i < sentence.size(); i++) {
				if (t[0].equals(sentence.get(i)[2])) {
					return new Boundary(i, i);
				}
			}
		}
		return null;*/
	}

	private Boundary ngramMatcher(String[] tokenizedRole, List<String[]> sentence, int n) {
		logger.debug(Arrays.toString(tokenizedRole) + "\t" + n);

		if (n > sentence.size()) {
			return null;
		}
		for (int i = 0; i < sentence.size() - n + 1; i++) {
			boolean b = true;
			for (int j = 0; j < n; j++) {
				logger.trace(i + "," + j + "\t" + tokenizedRole[j] + "\t" + sentence.get(i)[2]);
				//b &= tokenizedRole[j].equalsIgnoreCase(sentence.get(i + j)[2]);

				//replace with kernel function
				b &= equals(tokenizedRole[j].toLowerCase(), (sentence.get(i + j)[2].toLowerCase()));
				logger.trace(i + "," + j + "\t" + tokenizedRole[j] + "\t" + sentence.get(i + j)[2] + "\t" + tokenizedRole[j].equals(sentence.get(i + j)[2]));
			}
			if (b) {
				logger.trace("boundary(" + n + "): " + i + ", " + (i + n - 1));
				return new Boundary(i, i + n - 1);
			}

		}
		return null;
	}

	private boolean equals(String s, String t){
		double lambda = 1;
		int length=3;
		int min = Math.min(s.length(), t.length());
		if (min<length){
			length=min;
		}
		CharKernel sk = new CharKernel(lambda, length);
		double kst = sk.get(s, t);
		double kss = sk.get(s, s);
		double ktt = sk.get(t, t);
		double knorm = kst / Math.sqrt(kss*ktt);
		logger.trace("k("+s + ", " + t + ")= " + knorm);
		if (knorm > 0.7){
			logger.debug("k("+s + ", " + t + ")= " + knorm);
				return true;
		}
		return false;
	}
	private Map<Integer, String> readTraining(File f) throws IOException {
		Map<Integer, String> map = new TreeMap<Integer, String>();

		LineNumberReader lr = new LineNumberReader(new InputStreamReader(new FileInputStream(f), "UTF-8"));
		String line = null;
		StringBuilder sb = new StringBuilder();
		int id = -1;
		while ((line = lr.readLine()) != null) {
			String[] s = line.split("\t");
			if (s.length > 0 && s[0].length() > 0 && !s[0].equals("sid")) {
				sb.append(line + "\n");
				id = Integer.parseInt(s[0]);
			}
			else {
				if (sb.length() > 0) {
					map.put(id, sb.toString());
				}

				sb = new StringBuilder();
			}

		}
		map.put(id, sb.toString());
		return map;
	}

	public static void main(String[] args) {
		String logConfig = System.getProperty("log-config");
		if (logConfig == null) {
			logConfig = "log-config.txt";
		}

		Options options = new Options();
		options.addOption("h", "help", false, "print this message");
		options.addOption("v", "version", false, "output version information and exit");
		options.addOption(OptionBuilder.withDescription("trace mode").withLongOpt("trace").create());
		options.addOption(OptionBuilder.withDescription("debug mode").withLongOpt("debug").create());
		options.addOption(OptionBuilder.withDescription("info mode").withLongOpt("info").create());
		options.addOption(OptionBuilder.withArgName("file").hasArg().withDescription("file from which to read the labelled training set in tabular format (reference annotation)").isRequired().withLongOpt("labelled").create("l"));
		options.addOption(OptionBuilder.withArgName("file").hasArg().withDescription("file from which to read the translated unlabelled training set in tabular format (one sentence per line, including id)").isRequired().withLongOpt("unlabelled").create("u"));
		options.addOption(OptionBuilder.withArgName("file").hasArg().withDescription("file from which to read the translated roles (phrase table: source language \\t target language)").isRequired().withLongOpt("roles").create("r"));
		options.addOption(OptionBuilder.withArgName("file").hasArg().withDescription("file in which to write the translated labelled training set in tabular format (aligned with the reference annotation)").isRequired().withLongOpt("output").create("o"));
		options.addOption(OptionBuilder.withArgName("int").hasArg().withDescription("example from which to start from").withLongOpt("start").create());

		CommandLineParser parser = new PosixParser();
		CommandLine commandLine = null;

		try {
			commandLine = parser.parse(options, args);

			Properties defaultProps = new Properties();
			try {
				defaultProps.load(new InputStreamReader(new FileInputStream(logConfig), "UTF-8"));
			} catch (Exception e) {
				defaultProps.setProperty("log4j.appender.stdout", "org.apache.log4j.ConsoleAppender");
				defaultProps.setProperty("log4j.appender.stdout.layout.ConversionPattern", "[%t] %-5p (%F:%L) - %m %n");
				defaultProps.setProperty("log4j.appender.stdout.layout", "org.apache.log4j.PatternLayout");
				defaultProps.setProperty("log4j.appender.stdout.Encoding", "UTF-8");
			}

			if (commandLine.hasOption("trace")) {
				defaultProps.setProperty("log4j.rootLogger", "trace,stdout");
			}
			else if (commandLine.hasOption("debug")) {
				defaultProps.setProperty("log4j.rootLogger", "debug,stdout");
			}
			else if (commandLine.hasOption("info")) {
				defaultProps.setProperty("log4j.rootLogger", "info,stdout");
			}
			else {
				if (defaultProps.getProperty("log4j.rootLogger") == null) {
					defaultProps.setProperty("log4j.rootLogger", "info,stdout");
				}
			}
			PropertyConfigurator.configure(defaultProps);

			if (commandLine.hasOption("help") || commandLine.hasOption("version")) {
				throw new ParseException("");
			}

			File labelled = new File(commandLine.getOptionValue("labelled"));
			File unlabelled = new File(commandLine.getOptionValue("unlabelled"));
			File roles = new File(commandLine.getOptionValue("roles"));
			File output = new File(commandLine.getOptionValue("output"));
			try {
				if (commandLine.hasOption("start")){
					int start = Integer.parseInt(commandLine.getOptionValue("start"));
					new AnnotationMigration(labelled, unlabelled, roles, output, start);
				} else {
					new AnnotationMigration(labelled, unlabelled, roles, output);
				}


			} catch (IOException e) {
				logger.error(e);
			}

		} catch (ParseException exp) {
			if (exp.getMessage().length() > 0) {
				System.err.println("Parsing failed: " + exp.getMessage() + "\n");
			}
			HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp(200, "java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.AnnotationMigration", "\n", options, "\n", true);
			System.exit(1);
		}
	}
}