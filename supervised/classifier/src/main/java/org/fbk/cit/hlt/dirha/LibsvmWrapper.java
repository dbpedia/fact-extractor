package org.fbk.cit.hlt.dirha;

import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.LineNumberReader;
import java.util.Arrays;

/**
 * Created with IntelliJ IDEA.
 * User: giuliano
 * Date: 11/21/13
 * Time: 4:34 PM
 * To change this template use File | Settings | File Templates.
 */
public class LibsvmWrapper {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>LibsvmWrapper</code>.
	 */
	static Logger logger = Logger.getLogger(LibsvmWrapper.class.getName());

	public LibsvmWrapper(String[] parameters) {

		StringBuilder sb = new StringBuilder();
		for (int i = 0; i < parameters.length; i++) {
			sb.append(" ");
			sb.append(parameters[i]);
		}
		String[] cmd = new String[]{"/bin/sh",
				"-c", "./svm-train" + sb.toString()};
		//String[] fullCmd = new String[cmd.length + parameters.length];
		//System.arraycopy(cmd, 0, fullCmd, 0, cmd.length);
		//System.arraycopy(parameters, 0, fullCmd, cmd.length, parameters.length);
		logger.debug(Arrays.toString(cmd));
		Process p = null;
		try {
			p = Runtime.getRuntime().exec(cmd);
			logger.info("libsvm...");
			p.waitFor();
			int exitValue = p.exitValue();

			InputStream is = p.getInputStream();
			LineNumberReader lnr = new LineNumberReader(new InputStreamReader(is));
			String line;
			StringBuilder sb1 = new StringBuilder();
			while ((line = lnr.readLine()) != null) {
				sb1.append(line);
				sb1.append("\n");
			}
			logger.info(sb1.toString());

			logger.info("libsvm exit value: " + exitValue);
			if (exitValue != 0) {
				is = p.getErrorStream();
				lnr = new LineNumberReader(new InputStreamReader(is));
				sb = new StringBuilder();
				while ((line = lnr.readLine()) != null) {
					sb.append(line);
					sb.append("\n");
				}
				logger.error(sb.toString());
			}
		} catch (IOException e) {
			logger.error(e);
		} catch (InterruptedException e) {
			logger.error(e);
		}
	}

	public static void main(String[] args) {
		String logConfig = System.getProperty("log-config");
		if (logConfig == null) {
			logConfig = "log-config.txt";
		}
		PropertyConfigurator.configure(logConfig);

		//java -Dfile.encoding=UTF-8 -cp dist/dirha.jar  org.fbk.cit.hlt.dirha.LibsvmWrapper
		if (args.length > 0) {
			new LibsvmWrapper(args);
		}

	}
}
