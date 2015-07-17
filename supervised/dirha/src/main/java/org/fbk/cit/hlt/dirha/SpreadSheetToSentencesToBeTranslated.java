package org.fbk.cit.hlt.dirha;

import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;
import org.apache.commons.cli.*;
import org.fbk.cit.hlt.core.util.HashMultiSet;
import org.fbk.cit.hlt.core.util.MultiSet;

import java.io.*;
import java.util.*;

/**
 * Created with IntelliJ IDEA.
 * User: giuliano
 * Date: 9/4/14
 * Time: 8:00 AM
 *
 * This class takes as input the original training set in tabular format (Italian) and converts
 * it sentences, one per lines in HTML format.
 * It is used to translate the training data in other languages.
 *
 * After this step the *.sentences.html and *.terms.html must be translated using
 * Google Translate (https://translate.google.com).
 *
 * The translate sentences must be saved in a tsv file (id \t sentences).
 * The terms in a tsv file (it-term \t other-lang-term).
 *
 * Then use AnnotationMigration to create the training in the other language.
 *
 * @see AnnotationMigration
 * @see TranslatedSentencesToSpreadSheet
 */
public class SpreadSheetToSentencesToBeTranslated {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>SpreadSheetToSentencesToBeTranslated</code>.
	 */
	static Logger logger = Logger.getLogger(SpreadSheetToSentencesToBeTranslated.class.getName());

	private boolean isSpace(String sentence, String token) {
		return sentence.length() != 0 && !sentence.toString().endsWith("′") && !token.equals("′") && !sentence.toString().endsWith("/") && !token.equals("/") && !token.equals("!") && !token.equals("?") && !token.equals(".");
	}

	public SpreadSheetToSentencesToBeTranslated(File in, String root, String format) throws IOException {
		LineNumberReader lr = new LineNumberReader(new InputStreamReader(new FileInputStream(in), "UTF-8"));
		File html = new File(root + ".sentences.html");
		File referenceAnnotationTsv = new File(root + ".reference-annotation.tsv");
		File terms = new File(root + ".terms.html");
		PrintWriter sentencesHtmlWriter = new PrintWriter(new BufferedWriter(new OutputStreamWriter(new FileOutputStream(html), "UTF-8")));
		PrintWriter referenceAnnotationWriter = new PrintWriter(new BufferedWriter(new OutputStreamWriter(new FileOutputStream(referenceAnnotationTsv), "UTF-8")));
		PrintWriter termsHtmlWriter = new PrintWriter(new BufferedWriter(new OutputStreamWriter(new FileOutputStream(terms), "UTF-8")));

		String line = null;

		sentencesHtmlWriter.println("<!DOCTYPE html>");
		sentencesHtmlWriter.println("<html>");
		sentencesHtmlWriter.println("<head>");
		sentencesHtmlWriter.println("<title>Dirha speech understanding examples</title>");
		sentencesHtmlWriter.println("<meta charset=\"UTF-8\">");
		sentencesHtmlWriter.println("</head>");
		sentencesHtmlWriter.println("<body>");
		sentencesHtmlWriter.println("<table>");
		StringBuilder sentence = new StringBuilder();
		MultiSet<String> termSet = new HashMultiSet<String>();
		String role = null, prevRole = null;
		int id = 0;
		while ((line = lr.readLine()) != null) {
			String[] token = line.split("\t");

			if (token.length > 6) {
				logger.debug(Arrays.toString(token));

				try {
					int sid = Integer.parseInt(token[0]);
					//if (sentence.length() != 0 && !sentence.toString().endsWith("′") && !token[2].equals("′") && !sentence.toString().endsWith("/") && !token[2].equals("/") && !token[2].equals("!") && !token[2].equals("?") && !token[2].equals(".")) {
					if (isSpace(sentence.toString(), token[2])){
						sentence.append(" ");
					}
					if (sentence.toString().endsWith("po′")) {
						sentence.append(" ");
					}

					if (token[6].toLowerCase().startsWith("b-")) {
						//logger.debug("a\t\t" + role);
						if (role != null) {
							termSet.add(replace(role));
							logger.warn(role);
						}
						role = new String(token[2].toLowerCase());
					}
					else if (token[6].toLowerCase().startsWith("i-")) {
						//logger.debug("b\t\t" + role);
						//prevRole.setName(prevRole.getValue().substring(2, prevRole.getName().length()));
						if (role != null) {
							if (isSpace(role, token[2])){
								role+=" ";
							}
							role+=token[2];
							//role += " " + token[2];
						}
					}

					sentence.append(token[2]);
				} catch (NumberFormatException e) {
					//logger.error(e);
					if (role != null) {
						termSet.add(replace(role));
						role = null;
					}

					if (sentence.length() > 0) {
						logger.info(id + "\t" + replace(sentence.toString().trim()));
						sentencesHtmlWriter.print("<tr><td>");
						sentencesHtmlWriter.print(id);
						sentencesHtmlWriter.print("</td><td>");
						sentencesHtmlWriter.print(replace(sentence.toString().trim()).toLowerCase());
						sentencesHtmlWriter.println("</td></tr>");

						sentence = new StringBuilder();
						id++;
					}
				} finally {
					if (!token[0].equals("sid")) {
						referenceAnnotationWriter.println(id + "\t" + token[1] + "\t" + token[2].toLowerCase() + "\t" + token[3] + "\t" + token[4] + "\t" + token[5] + "\t" + token[6]);
					}
					else {
						referenceAnnotationWriter.print("\n");
					}

				}

			}
		}
		logger.info(id + "\t" + sentence.toString().trim());
		sentencesHtmlWriter.print("<tr><td>");
		sentencesHtmlWriter.print(id);
		sentencesHtmlWriter.print("</td><td>");
		sentencesHtmlWriter.print(replace(sentence.toString().trim()).toLowerCase());
		sentencesHtmlWriter.println("</td></tr>");

		sentencesHtmlWriter.println("<table>");
		sentencesHtmlWriter.println("</body>");
		sentencesHtmlWriter.println("</html>");
		sentencesHtmlWriter.close();
		referenceAnnotationWriter.close();

		//terms
		termsHtmlWriter.println("<!DOCTYPE html>");
		termsHtmlWriter.println("<html>");
		termsHtmlWriter.println("<head>");
		termsHtmlWriter.println("<title>Dirha speech understanding examples</title>");
		termsHtmlWriter.println("<meta charset=\"UTF-8\">");
		termsHtmlWriter.println("</head>");
		termsHtmlWriter.println("<body>");
		termsHtmlWriter.println("<table>");

		SortedMap<Integer, List<String>>sortedTermMap=  termSet.toSortedMap();
		Iterator<Integer> iterator = sortedTermMap.keySet().iterator();
		while (iterator.hasNext()) {
			int f = iterator.next();
			List<String> list = sortedTermMap.get(f);
			for (int i = 0; i < list.size(); i++) {
				termsHtmlWriter.print("<tr><td>");
				termsHtmlWriter.print(f);
				termsHtmlWriter.print("</td><td>");
				termsHtmlWriter.print(replace(list.get(i)).toLowerCase());
				termsHtmlWriter.println("</td></tr>");

			}
		}
		termsHtmlWriter.println("<table>");
		termsHtmlWriter.println("</body>");
		termsHtmlWriter.println("</html>");
		termsHtmlWriter.close();
		logger.debug(termSet);
	}

	private String replace(String s) {
		return s.replaceAll("′", "'").replaceAll("po'", "po").replaceAll("/ ", "/");
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
		options.addOption(OptionBuilder.withArgName("file").hasArg().withDescription("file from which to read the training set in tabular format").isRequired().withLongOpt("training").create("t"));
		options.addOption(OptionBuilder.withArgName("file").hasArg().withDescription("root of files in which to write the sentences").isRequired().withLongOpt("sentences").create("s"));
		options.addOption(OptionBuilder.withArgName("string").hasArg().withDescription("format (html or text)").withLongOpt("format").create("f"));

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
			else {
				if (defaultProps.getProperty("log4j.rootLogger") == null) {
					defaultProps.setProperty("log4j.rootLogger", "info,stdout");
				}
			}
			PropertyConfigurator.configure(defaultProps);

			if (commandLine.hasOption("help") || commandLine.hasOption("version")) {
				throw new ParseException("");
			}

			File in = new File(commandLine.getOptionValue("training"));
			String root = commandLine.getOptionValue("sentences");
			String format = commandLine.getOptionValue("format");
			try {
				new SpreadSheetToSentencesToBeTranslated(in, root, format);
			} catch (IOException e) {
				logger.error(e);
			}

		} catch (ParseException exp) {
			if (exp.getMessage().length() > 0) {
				System.err.println("Parsing failed: " + exp.getMessage() + "\n");
			}
			HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp(200, "java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.SpreadSheetToSentencesToBeTranslated", "\n", options, "\n", true);
			System.exit(1);
		}

	}
}