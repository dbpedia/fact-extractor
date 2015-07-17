package org.fbk.cit.hlt.dirha.kernel;

import org.apache.log4j.Logger;

import java.util.ArrayList;
import java.util.List;

/**
 * Created with IntelliJ IDEA.
 * User: giuliano
 * Date: 2/4/13
 * Time: 11:16 AM
 * To change this template use File | Settings | File Templates.
 */
public class Frame {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>Frame</code>.
	 */
	static Logger logger = Logger.getLogger(Frame.class.getName());

	String name;

	String target;

	List<Role> roleList;

	public Frame(String name, String target) {
		this.name = name;
		this.target = target;
		roleList = new ArrayList<Role>();
	}

	public void setRoleList(List<Role> roleList) {
		this.roleList = roleList;
	}

	public List<Role> getRoleList() {
		return roleList;
	}

	public void addRole(Role role)
	{
		roleList.add(role);
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getTarget() {
		return target;
	}

	public void setTarget(String target) {
		this.target = target;
	}

	@Override
	public boolean equals(Object o) {
		if (o instanceof Frame)
		{
			Frame f = (Frame) o;
			if (name.equals(f.getName()) && target.equals(f.getTarget()))
			{
				return true;
			}
		}
		return false;
	}

	@Override
	public String toString() {
		return "Frame{" +
						"name='" + name + '\'' +
						", target='" + target + '\'' +
						", roleList=" + roleList +
						'}';
	}
}
