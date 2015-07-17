package org.fbk.cit.hlt.dirha;

import org.apache.log4j.Logger;
//import org.apache.log4j.PropertyConfigurator;
import org.glassfish.grizzly.http.server.HttpHandler;
import org.glassfish.grizzly.http.server.Request;
import org.glassfish.grizzly.http.server.Response;
import org.apache.commons.lang.CharEncoding;

import java.io.IOException;
import java.io.OutputStream;
import java.io.UnsupportedEncodingException;
import java.text.DecimalFormat;
import java.util.Date;
import java.util.Iterator;

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
 * Date: 12/4/13
 * Time: 12:39 PM
 * To change this template use File | Settings | File Templates.
 */
public class AnnotationHttpHandler extends HttpHandler {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>AnnotationHttpHandler</code>.
	 */
	static Logger logger = Logger.getLogger(AnnotationHttpHandler.class.getName());
	private Annotator annotator;
	private String host;
	private String port;
	private static DecimalFormat tf = new DecimalFormat("000,000,000.#");
	private DirhaAnswerMapping dirhaAnswerMapping;

	public AnnotationHttpHandler(Annotator annotator, String host, String port, String lang) throws IOException {
		this.annotator = annotator;
		this.host = host;
		this.port = port;
		dirhaAnswerMapping = new DirhaAnswerMapping(lang);
	}

	private String request2string(Request request) {
		StringBuilder sb = new StringBuilder();
		sb.append("date=" + new Date() + "\n");
		sb.append("user=" + request.getRemoteUser() + "\n");
		sb.append("addr=" + request.getRemoteAddr() + "\n");
		sb.append("host=" + request.getRemoteHost() + "\n");
		sb.append("port=" + request.getRemotePort() + "\n");
		sb.append("method=" + request.getMethod() + "\n");
		sb.append("headers=" + request.getHeaderNames() + "\n");
		sb.append("authorization=" + request.getAuthorization() + "\n");
		sb.append("encoding=" + request.getCharacterEncoding() + "\n");
		sb.append("length=" + request.getContentLength() + "\n");
		sb.append("type=" + request.getContentType() + "\n");
		Iterator<String> it = request.getHeaderNames().iterator();
		for (int i = 0; it.hasNext(); i++) {
			String name = it.next();
			String value = request.getHeader(name);
			sb.append(name);
			sb.append("=");
			sb.append(value);
			sb.append("\n");
		}
		return sb.toString();
	}

	@Override
	public void service(Request request, Response response) throws Exception {
		long begin = System.nanoTime();
		logger.debug("frame annotation service");
		logger.debug("request " + request);
		//response.setContentType("text/plain");
		response.setContentType("text/html");
		//response.setCharacterEncoding(CharEncoding.ISO_8859_1);
		response.setCharacterEncoding(CharEncoding.UTF_8);
		logger.debug(request2string(request));

		if (request.getParameter("shutdown") != null) {
			logger.info("shut down on " + new Date());
			OutputStream os = response.getOutputStream();
			response.setStatus(200);
			//if (callback == null) {
			//os.write(new String("shutdown now (" + new Date() + ")").getBytes(CharEncoding.ISO_8859_1));
			os.write(new String("shutdown now (" + new Date() + ")").getBytes(CharEncoding.UTF_8));
			//}
			//else {
			//	os.write((callback + "(" + result + ")").getBytes(CharEncoding.UTF_8));
			//}
			os.flush();
			System.exit(0);
		}
		//String text = request.getParameter("text");
		String text = getParameter("text", request);
		if (text == null){
			OutputStream os = response.getOutputStream();
			response.setStatus(200);
			os.write(new String("date=" + new Date()).getBytes(CharEncoding.UTF_8));
			os.flush();
		}
		text = replaceText(text);

		String result = "";
		logger.debug(host + ":"+port);
		//"<meta charset=\"UTF-8\">\n"+
		//enctype="text/plain" accept-charset="UTF-8"
		//<!DOCTYPE html>
		Answer answer = annotator.classify(text);
		if (request.getParameter("production") != null){
			Sentence sentence = answer.getSentence();
			logger.debug(sentence);
			Sentence collapsedSentence = sentence.collapse();
			logger.debug(collapsedSentence);
			result += dirhaAnswerMapping.print(collapsedSentence, DirhaAnswerMapping.TXT );

		} else {
			if (request.getParameter("demo") != null) {
				result += "<html><head>\n" +
						"    <title>Dirha text understanding demo</title>\n" +
						"<meta charset=\"UTF-8\">\n"+
						//"<meta http-equiv=\"content-type\" content=\"text/html; charset=ISO-8859-1\">\n"+
						"<!--" + host + ":"+port + "-->\n"+
						"</head>" + "<body>\n" +
						//.super.
						//"<form name=\"input\" action=\"http://" + host + ":" + port + "/tu\" method=\"post\" accept-charset=\"ISO-8859-1\">\n" +
						"<form name=\"input\" action=\"http://" + host + ":" + port + "/tu\" method=\"post\" accept-charset=\"UTF-8\">\n" +
						"<input type=\"hidden\" name=\"demo\" value=\"1\">\n" +
						"<textarea cols=\"40\" rows=\"5\" name=\"text\">" +

						(text != null ? text : "Apri le finestre della camera da letto") +
						"</textarea>\n" +
						"    <input type=\"submit\" value=\"Submit\">\n" +
						"</form>";
			}


			logger.debug("text " + text);
			if (text != null) {
				result += "<p>" + answer.toHtml() + "</p>";
				Sentence sentence = answer.getSentence();
				logger.debug(sentence);
				Sentence collapsedSentence = sentence.collapse();
				logger.debug(collapsedSentence);
				result += "\n" + "<p>" + dirhaAnswerMapping.print(collapsedSentence, DirhaAnswerMapping.HTML) + "</p>";
			}
			else {
				result += "<p>Error: text not specified</p>";
				response.setStatus(400);
			}


			if (request.getParameter("demo") != null) {
				result += "</body>\n" +
						"</html>";
			}

		}
		logger.debug("result " + result);
		//String callback = request.getParameter("callback");

		OutputStream os = response.getOutputStream();
		response.setStatus(200);
		//if (callback == null) {
		//byte[] bytes = result.getBytes(CharEncoding.ISO_8859_1);
		byte[] bytes = result.getBytes(CharEncoding.UTF_8);
		//response.setContentLength(bytes.length);
		os.write(bytes);

		long end = System.nanoTime();
		logger.info("done in " + tf.format(end - begin) + " ns");
		//}
		//else {
		//	os.write((callback + "(" + result + ")").getBytes(CharEncoding.UTF_8));
		//}
		os.flush();
	}

	/*private String exception1() throws IOException {
		logger.debug("exception1");
		String result = "<p>Put_into_operation: [accendi]<sub>LU</sub> la [luce]<sub>Device</sub></p>\n" +
				"<p>Semantics_action: turnOn</br>Semantics_class: light</br></p>";
		return result;
	} */

	private String replaceText(String text) {
		if (text!=null){
			return text.toLowerCase().replaceAll("e'", "è");
		}
		return text;
	}
	/**
	 * Because Grizzly behaves strange (different from tomcat for example) with
	 * parameter given in the URL with utf-8 encoding, we create a unique and
	 * common method that handle correctly this problems. It may be a bug. In
	 * the future only one place is necessary to change when changing container
	 * of after grizzly bug fix.
	 *
	 * @return
	 * @throws java.io.UnsupportedEncodingException
	 */
	private String getParameter(String name, Request request) {
		if (request.getMethod().getMethodString().equalsIgnoreCase("get")) {
			return readRawUtf8String(request.getParameter(name));
		}
		if (request.getMethod().getMethodString().equalsIgnoreCase("post")) {
			String queryString = request.getQueryString();
			if (queryString != null) {
				throw new IllegalStateException("If you use post don't use parameters on the url. Give all the parameters in the input stream!");
			}
			String postParameter = request.getParameter(name);
			// Post parameter does not need of utf8 encoding! If needed is because the utf-8 was not specified
			// in the post Content type header
			// connection.setRequestProperty("Content-type", "application/x-www-form-urlencoded; charset=UTF-8");
			// postParameter = readRawUtf8String(postParameter);
			return postParameter;
		}
		throw new IllegalStateException("Only get or post supported!");
	}

	private static String readRawUtf8String(String rawUtf8String) {
		if (rawUtf8String == null) {
			return null;
		}
		byte[] rawUtf8Bytes = new byte[rawUtf8String.length()];
		for (int i = 0; i < rawUtf8Bytes.length; i++) {
			int c = rawUtf8String.charAt(i);
			if (c > 255 || c < 0) {
				// I use a runtime exception, because reading parameter must be
				// present, I am handling a bug!
				throw new RuntimeException("Unexpected utf-8 value!");
			}
			rawUtf8Bytes[i] = (byte) c;
		}
		try {
			return new String(rawUtf8Bytes, CharEncoding.UTF_8);
		} catch (UnsupportedEncodingException encxxx) {
			// I use a runtime exception, because reading parameter must be
			// present, I am handling a bug!
			throw new RuntimeException("Unexpected utf-8 exception!", encxxx);
		}
	}
}
