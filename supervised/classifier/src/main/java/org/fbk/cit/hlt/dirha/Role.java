package org.fbk.cit.hlt.dirha;

import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;

/**
 * Created with IntelliJ IDEA.
 * User: giuliano
 * Date: 1/24/14
 * Time: 10:54 AM
 * To change this template use File | Settings | File Templates.
 */
public class Role {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>Role</code>.
	 */
	static Logger logger = Logger.getLogger(Role.class.getName());

	private String id;
	private String name;
	private String value;

	Role(Role role) {
		this.id = role.getId();
		this.name = role.getName();
		this.value = role.getValue();
	}

	Role(String id, String name, String value) {
		this.id = id;
		this.name = name;
		this.value = value;
	}

	void setId(String id) {
		this.id = id;
	}

	void setName(String name) {
		this.name = name;
	}

	void setValue(String value) {
		this.value = value;
	}

	String getName() {
		return name;
	}

	String getValue() {
		return value;
	}

	String getId() {
		return id;
	}

	@Override
	public boolean equals(Object o) {

		if (this == o) {
			logger.debug("T " + this + " equals " + o);
			return true;
		}
		if (!(o instanceof Role)) {
			logger.debug("F " + this + " equals " + o);
			return false;
		}

		Role role = (Role) o;

		if (name != null ? !name.equals(role.name) : role.name != null) {
			logger.debug("F " + this + " equals " + o);
			return false;
		}
		if (value != null ? !value.equals(role.value) : role.value != null) {
			logger.debug("F " + this + " equals " + o);
			return false;
		}

		logger.debug("T " + this + " equals " + o);
		return true;
	}

	@Override
	public int hashCode() {
		logger.debug("hashCode" + this);
		int result = name != null ? name.hashCode() : 0;
		result = 31 * result + (value != null ? value.hashCode() : 0);
		return result;
	}

	@Override
	public String toString() {
		return "Role{" +
				"id=" + id +
				", name='" + name + '\'' +
				", value='" + value + '\'' +
				'}';
	}
}
