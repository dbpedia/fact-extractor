package org.fbk.cit.hlt.dirha;

import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;

import java.util.*;

/**
 * Created with IntelliJ IDEA.
 * User: giuliano
 * Date: 1/24/14
 * Time: 10:53 AM
 * To change this template use File | Settings | File Templates.
 */
public class Sentence {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>Sentence</code>.
	 */
	static Logger logger = Logger.getLogger(Sentence.class.getName());

	private Map<String, List<Role>> frameMap;
	private int id;


	Sentence(int id) {
		this.id = id;
		frameMap = new HashMap<String, List<Role>>();
	}

	int getId() {
		return id;
	}

	public Set<String> frames() {
		return frameMap.keySet();
	}

	public void add(int id, String frame, String role, String value) {
		//logger.debug("adding role " + frame + "\t" + role + "\t" + value);
		if (frame == null||frame.length() == 0 || frame.equalsIgnoreCase("o")) {
			return;
		}
		List<Role> roleList = frameMap.get(frame);
		if (roleList == null) {
			roleList = new ArrayList<Role>();
			frameMap.put(frame, roleList);
		}
		roleList.add(new Role(id, role, value));
	}

	protected void add(String frame, List<Role> roles) {
		frameMap.put(frame, roles);
	}


	public List<Role> getRoleList(String frame) {
		return frameMap.get(frame);
	}

	public Sentence collapse() {
		//logger.debug("collapse");
		Sentence sentence = new Sentence(id);
		Iterator<String> it = frames().iterator();
		for (int i = 0; it.hasNext(); i++) {
			String frame = it.next();

			List<Role> roles = collapseRoles(getRoleList(frame));
			//logger.debug(frame + "\t" + roles);
			sentence.add(frame, roles);
		}
		//logger.debug("collapse");
		//logger.debug(sentence);
		return sentence;
	}

	List<Role> collapseRoles(List<Role> roleList) {
		//logger.debug("before\t" + roleList);

		List<Role> list = new ArrayList<Role>();
		if (roleList == null) {
			return list;
		}
		Role prevRole = null;
		for (int i = 0; i < roleList.size(); i++) {
			Role role = roleList.get(i);
			//logger.debug(i + "\t" + role);
			if (role.getName().startsWith("B-")) {
				//logger.debug("a\t\t" + role);
				prevRole = new Role(role);
				list.add(prevRole);
			}
			else if (role.getName().startsWith("I-")) {
				//logger.debug("b\t\t" + role);

				if (prevRole == null) {
					prevRole = new Role(role);
				}
				prevRole.setValue(prevRole.getValue() + " " + role.getValue());
			}
		}
		//logger.debug("after\t" + list);
		return list;
	}

	@Override
	public String toString() {
		StringBuilder sb = new StringBuilder();
		Iterator<String> it = frames().iterator();
		for (int i = 0; it.hasNext(); i++) {
			String frame = it.next();
			List<Role> roles = frameMap.get(frame);
			sb.append(frame);
			sb.append("\t");
			sb.append(roles);
			sb.append("\n");
		}
		return sb.toString();
	}
}
