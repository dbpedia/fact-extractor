package org.fbk.cit.hlt.dirha.kernel;

import org.apache.log4j.Logger;

/**
 * Created with IntelliJ IDEA.
 * User: giuliano
 * Date: 2/4/13
 * Time: 2:59 PM
 * To change this template use File | Settings | File Templates.
 */
public class Role {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>Role</code>.
	 */
	static Logger logger = Logger.getLogger(Role.class.getName());

	String name;

	String arg;

	public Role(String name, String arg) {
		this.name = name;
		this.arg = arg;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getArg() {
		return arg;
	}

	public void setArg(String arg) {
		this.arg = arg;
	}

	@Override
	public boolean equals(Object o) {
		if (o instanceof Role)
		{
			Role r = (Role) o;
			if (name.equals(r.getName()) && arg.equals(r.getArg()))
			{
				return true;
			}
		}
		return false;
	}

	@Override
	public String toString() {
		return "Role{" +
						"name='" + name + '\'' +
						", arg='" + arg + '\'' +
						'}';
	}
}
