package org.fbk.cit.hlt.dirha;

import org.apache.commons.lang.StringEscapeUtils;
import org.apache.log4j.Logger;
import org.fbk.cit.hlt.core.analysis.tokenizer.HardTokenizer;
import org.fbk.cit.hlt.core.analysis.tokenizer.Tokenizer;

import java.io.*;
import java.util.*;

/**
 * Created with IntelliJ IDEA.
 * User: giuliano
 * Date: 1/24/14
 * Time: 10:50 AM
 * <p/>
 * To port, modify:
 * <p/>
 * device-semantic-class
 */
public class DirhaAnswerMapping {

	//todo: mapping ' -> '
	//todo: house,...
	//
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>DirhaAnswerMapping</code>.
	 */
	static Logger logger = Logger.getLogger(DirhaAnswerMapping.class.getName());

	//private Map<String, String> maps;

	private Map<String, Map<String, String>> maps;

	private Map<String, String> lists;
	private String lang;

	public final static int HTML = 0;

	public final static int TXT = 1;

	//private Sentence collapsedSentence;

	public DirhaAnswerMapping(String lang) throws IOException {
		this.lang = lang;
		//maps = new HashMap<String, String>();
		File resources = new File("./resources/" + lang);
		//readLists(resources);
		readMaps(resources);
		readLists(resources);
	}

	private void readMaps(File resources) throws IOException {
		logger.debug("reading maps from " + resources + "...");
		maps = new HashMap<String, Map<String, String>>();

		File[] files = resources.listFiles(new FileFilter() {
			@Override
			public boolean accept(File pathname) {
				return pathname.getAbsolutePath().endsWith(".map");
			}
		});
		for (int i = 0; i < files.length; i++) {
			String name = files[i].getName();
			int j = name.indexOf('.');
			String value = name.substring(0, j);
			maps.put(value, readMap(files[i]));
			//add(value, files[i]);

		}
	}

	public String print(Sentence sentence, int type) {
		StringBuilder sb = new StringBuilder();
		Set<String> set = sentence.frames();
		Iterator<String> it = set.iterator();
		// iterates over frames
		for (int i = 0; it.hasNext(); i++) {
			String frame = it.next();

			//if (frame.equals(""))
			List<Role> roles = sentence.getRoleList(frame);
			//Map<String, String> map = maps.get("frame");

			if (frame.equals("Activation")) {
				//todo: rename
				//if (lang.equalsIgnoreCase("it")){
				//sb.append("KWS: dirha attivati</br>");
				print("KWS=dirha attivati", sb, type);
				//}

			}
			else if (frame.equals("Confirm")) {
				logger.warn(roles);

				// iterates over roles
				for (int j = 0; j < roles.size(); j++) {
					Role role = roles.get(j);

					logger.debug(i + "\t" + j + "\t" + frame + "\t" + role + "\t" + lists.get(role.getValue()));
					if (role.getName().equals("B-LU")) {
						String mappedValue = role.getValue().toLowerCase();
						logger.trace(j + "\t" + role + "\t" + mappedValue);
						//sb.append("Semantics_confirm: " + lists.get(mappedValue) + "</br>");
						print("Semantics_confirm=" + lists.get(mappedValue), sb, type);
					} else if (role.getName().equals("B-Place")) {
						logger.trace(j + "\t" + role + "\t" +  role.getValue());
						//sb.append("Semantics_location: " +  role.getValue() + "</br>");
						print("Semantics_location=" +  role.getValue(), sb, type);
					} else if (role.getName().equals("B-Device")) {
						logger.trace(j + "\t" + role + "\t" +  role.getValue());
						//sb.append("Semantics_class: " +  role.getValue() + "</br>");
						print("Semantics_class=" +  role.getValue(), sb, type);
					} else if (role.getName().equals("B-Value")) {
						logger.trace(j + "\t" + role + "\t" +  role.getValue());
						//sb.append("Semantics_class: " +  role.getValue() + "</br>");
						print("Semantics_action_attr=" +  role.getValue(), sb, type);
					}  else if (role.getName().equals("B-Property")) {
						logger.trace(j + "\t" + role + "\t" +  role.getValue());
						//sb.append("Semantics_class: " +  role.getValue() + "</br>");
						print("Semantics_class=" +  role.getValue(), sb, type);
					}
				}
			}
			else {
				//sb.append("Semantics_action: " + maps.get("frame").get(frame.toLowerCase()) + "</br>");
				print("Semantics_action=" + maps.get("frame").get(frame.toLowerCase()), sb, type);
				logger.debug("Semantics_action: " + maps.get("frame").get(frame.toLowerCase()));
				// iterates over roles
				for (int j = 0; j < roles.size(); j++) {
					Role role = roles.get(j);

					logger.debug("Role\t" + i + "\t" + j + "\t" + frame + "\t" + role + "\t" + lists.get(role.getValue()));
					if (role.getName().equals("B-Device")) {
						Tokenizer tokenizer = new HardTokenizer();
						String[] tokens = tokenizer.stringArray(role.getValue().toLowerCase());

						for (int k = 0; k < tokens.length; k++) {
							logger.debug(k + "\t" + tokens[k]);
							//String mappedRole = lists.get(role.getName());
							String deviceSemanticClass = maps.get("device-semantic-class").get(tokens[k].toLowerCase());
							String attributeSemanticClass = maps.get("device-semantic-attribute").get(tokens[k].toLowerCase());
							logger.trace(i + "\t" + j + "\t" + k + "\t" + deviceSemanticClass + "\t" + attributeSemanticClass);
							if (deviceSemanticClass != null) {
								String mappedValue = lists.get(tokens[k]);
								//sb.append(deviceSemanticClass + ": " + mappedValue + "</br>");
								print(deviceSemanticClass + "=" + mappedValue, sb, type);
							}
							if (attributeSemanticClass != null) {
								String mappedValue = lists.get(tokens[k]);
								//sb.append(attributeSemanticClass + ": " + mappedValue + "</br>");
								print(attributeSemanticClass + "=" + mappedValue, sb, type);
							}
						}
					}
					else if (role.getName().equals("B-Value")) {
						logger.debug(">>\t" + role);
						String value = maps.get("value").get(role.getValue().toLowerCase());
						logger.debug(">>\t" + value);
						if (value != null) {
							//sb.append("Semantics_action_attr: " + value + "</br>");
							print("Semantics_action_attr=" + value, sb, type);
						}
					}
					else if (role.getName().equals("B-Place")) {

						//String mappedRole = lists.get(role.getName());
						String mappedValue = lists.get(role.getValue().toLowerCase());
						logger.trace(i + "\t" + j + "\t(" + role.getName() + ")\t" + mappedValue + " (" + role.getValue() + ")");

						// non trova i place mappedRole=null
						if (mappedValue != null) {
							//sb.append("Semantics_location: " + mappedValue + "</br>");
							print("Semantics_location=" + mappedValue, sb, type);
						}
					}
					else if (role.getName().equals("B-Property")) {

						//String mappedRole = lists.get(role.getName());
						String mappedValue = lists.get(role.getValue().toLowerCase());
						logger.trace(i + "\t" + j + "\t(" + role.getName() + ")\t" + mappedValue + " (" + role.getValue() + ")");

						// non trova i place mappedRole=null
						if (mappedValue != null) {
							//sb.append("Semantics_class: " + mappedValue + "</br>");
							print("Semantics_class=" + mappedValue, sb, type);
						}
					}
					else {

						String mappedRole = lists.get(role.getName());
						String mappedValue = lists.get(role.getValue().toLowerCase());
						logger.trace(i + "\t" + j + "\t" + mappedRole + " (" + role.getName() + ")\t" + mappedValue + " (" + role.getValue() + ")");

						// non trova i place mappedRole=null
						if (mappedRole != null && mappedValue != null) {
							//sb.append(mappedRole + ": " + mappedValue + "</br>");
							print(mappedRole + "=" + mappedValue, sb, type);
						}
					}
				}
			}
		}

		//return StringEscapeUtils.escapeHtml(sb.toString());
		return sb.toString();
	}

	void print(String text, StringBuilder sb, int type){
		if (type == HTML){
			sb.append(text + "</br>");
		} else if (type == TXT){
			sb.append(text + "\n");
		}
	}

	private Map<String, String> readMap(File f) {
		Map<String, String> map = new HashMap<String, String>();
		try {
			LineNumberReader lr = new LineNumberReader(new InputStreamReader(new FileInputStream(f), "UTF-8"));
			Set<String> set = new HashSet<String>();
			String line = null;
			List<Sentence> sentenceList = new ArrayList<Sentence>();
			String sid = null;
			int count = 0;
			Sentence sentence = null;

			while ((line = lr.readLine()) != null) {
				String[] s = line.trim().split("=");
				logger.debug(s[0].toLowerCase() + "\t" + s[1]);
				map.put(s[0].toLowerCase(), s[1].toLowerCase());

			}
		} catch (IOException e) {
			logger.error(e);
		}
		return map;
	}

	private void readLists(File resources) throws IOException {
		lists = new HashMap<String, String>();
		File[] files = resources.listFiles(new FileFilter() {
			@Override
			public boolean accept(File pathname) {
				return pathname.getAbsolutePath().endsWith(".list");
			}
		});
		for (int i = 0; i < files.length; i++) {
			String name = files[i].getName();
			int j = name.indexOf('.');
			String value = name.substring(0, j);
			add(value, files[i]);

		}
	}

	private void add(String value, File fin) throws IOException {
		LineNumberReader lr = new LineNumberReader(new InputStreamReader(new FileInputStream(fin), "UTF-8"));
		Set<String> set = new HashSet<String>();
		String line = null;
		List<Sentence> sentenceList = new ArrayList<Sentence>();
		String sid = null;
		int count = 0;
		Sentence sentence = null;
		while ((line = lr.readLine()) != null) {
			logger.debug(line + "\t" + value);
			lists.put(line.trim().toLowerCase(), value.toLowerCase());

		}
	}

}
