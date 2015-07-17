package org.fbk.cit.hlt.dirha;

import org.apache.commons.cli.*;
import org.apache.commons.lang.CharEncoding;
import org.apache.commons.lang.StringEscapeUtils;
import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;

import java.io.*;
import java.net.*;

/**
 * Created with IntelliJ IDEA.
 * User: giuliano
 * Date: 1/27/14
 * Time: 11:52 AM
 * To change this template use File | Settings | File Templates.
 */
public class HttpClient {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>HttpClient</code>.
	 */
	static Logger logger = Logger.getLogger(HttpClient.class.getName());

	public HttpClient(CommandLine line) {
		try {
			String serverCall = buildServerCall(line);
			URL serverAddress = buildServerAddress(line);
			if (line.hasOption("text")) {

				logger.info(serverAddress + "?" + serverCall);
				String answer = call(serverAddress, serverCall);
				logger.info("\n" + answer);
			}
		} catch (MalformedURLException e) {
			logger.error(e);
		} catch (ProtocolException e) {
			logger.error(e);
		} catch (IOException e) {
			logger.error(e);
		}
	}

	private String call(URL serverAddress, String serverCall) throws ProtocolException, IOException {
		String fromServer = null;
		// Set up the initial connection
		HttpURLConnection connection = (HttpURLConnection) serverAddress.openConnection();
		connection.setRequestMethod("POST");
		//connection.setRequestMethod("GET");
		//logger.debug(connection.getRequestMethod());
		connection.setRequestProperty("Content-type", "application/x-www-form-urlencoded; charset=UTF-8");
		connection.setDoOutput(true);
		//connection.setReadTimeout(10000);
		//connection.setConnectTimeout(10000);
		connection.getOutputStream().write(serverCall.getBytes(CharEncoding.UTF_8));
		connection.connect();
		//logger.debug(serverCall);

		// read the result from the server

		BufferedReader rd = new BufferedReader(new InputStreamReader(connection.getInputStream()));
		StringBuilder sb = new StringBuilder();
		while ((fromServer = rd.readLine()) != null) {
			sb.append(fromServer + '\n');
		}
		return sb.toString();
	}

	private URL buildServerAddress(CommandLine line) throws MalformedURLException {
		StringBuilder sbUrl = new StringBuilder();
		String host = line.getOptionValue("host");
		if (host == null) {
			host = Annotator.DEFAULT_HOST;
		}
		String port = line.getOptionValue("port");
		sbUrl.append("http://");
		sbUrl.append(host);
		if (port != null) {
			sbUrl.append(":");
			sbUrl.append(port);
		}
		sbUrl.append("/tu");
		return new URL(sbUrl.toString());
	}

	private String buildServerCall(CommandLine line) throws UnsupportedEncodingException {
		StringBuilder sb = new StringBuilder();

		String text = line.getOptionValue("text");
		if (text != null) {
			sb.append("text");
			sb.append("=");
			sb.append(URLEncoder.encode(text, CharEncoding.UTF_8));
		}
		return sb.toString();
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// java -cp dist/jservice.jar com.machinelinking.server.SimpleHttpClient
		String logConfig = System.getProperty("log-config");
		if (logConfig == null) {
			logConfig = "log-config.txt";
		}

		PropertyConfigurator.configure(logConfig);

		Options options = new Options();
		try {
			options.addOption(OptionBuilder.withArgName("string").hasArg().withDescription("host name (default is " + Annotator.DEFAULT_HOST + ")").withLongOpt("host").create("o"));
			options.addOption(OptionBuilder.withArgName("int").hasArg().withDescription("port number (default is " + Annotator.DEFAULT_PORT + ")").withLongOpt("port").create("p"));
			options.addOption(OptionBuilder.withArgName("string").hasArg().withDescription("text to annotate").withLongOpt("text").create("t"));

			options.addOption(OptionBuilder.withDescription("trace mode").withLongOpt("trace").create());
			options.addOption(OptionBuilder.withDescription("debug mode").withLongOpt("debug").create());

			options.addOption("h", "help", false, "print this message");
			options.addOption("v", "version", false, "output version information and exit");

			CommandLineParser parser = new PosixParser();


			// parse the command line arguments
			CommandLine line = parser.parse(options, args);

			if (line.getOptions().length == 0 || line.hasOption("help") || line.hasOption("version")) {
				throw new ParseException("");
			}

			new HttpClient(line);

		} catch (ParseException e) {
			// oops, something went wrong
			System.err.println("Parsing failed: " + e.getMessage() + "\n");
			HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp(200, "java -cp dist/dirha.jar org.fbk.cit.hlt.dirha.HttpClient", "\n", options, "\n", true);
		} catch (Exception e) {
			logger.error(e);
		}
	}
}
