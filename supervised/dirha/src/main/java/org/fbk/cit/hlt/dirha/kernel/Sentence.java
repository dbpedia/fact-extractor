package org.fbk.cit.hlt.dirha.kernel;

import org.apache.log4j.Logger;

import java.util.ArrayList;
import java.util.List;

/**
 * Created with IntelliJ IDEA.
 * User: giuliano
 * Date: 2/1/13
 * Time: 1:53 PM
 * To change this template use File | Settings | File Templates.
 */
public class Sentence {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>Sentence</code>.
	 */
	static Logger logger = Logger.getLogger(Sentence.class.getName());

	List<String> sentenceList;

	List<Frame> frameList;

	Sentence() {
		sentenceList = new ArrayList<String>();
		frameList = new ArrayList<Frame>();
	}

	public void addTokens(String[] s) {
		for (int i = 0; i < s.length; i++) {
			sentenceList.add(s[i]);
		}
	}

	public void addToken(String t) {
		sentenceList.add(t);
	}

	public List<Frame> getFrameList() {
		return frameList;
	}

	public void addFrame(Frame f)
	{
		frameList.add(f);
	}

	@Override
	public String toString() {
		StringBuilder sb = new StringBuilder();
		if (sentenceList.size() > 0)
		{
			sb.append(sentenceList.get(0));
		}

		for (int i = 1; i < sentenceList.size(); i++) {
			sb.append(" ");
			sb.append(sentenceList.get(i));
		}
		sb.append('\n');
		sb.append(frameList);
		sb.append('\n');
		return sb.toString();
	}
}
