package org.fbk.cit.hlt.dirha;

import java.io.*;
import java.util.*;
import org.apache.log4j.Logger;

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
 * This class implements a term index. Terms can be added to the index
 * and indexs are returned when querying with terms.
 * Consider if it could be implemented using lucene.
 *
 * @author		Claudio Giuliano
 * @version 	%I%, %G%
 * @since			1.0
 */
public class FeatureIndex
{
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>ngramIndex</code>.
	 */
	static Logger logger = Logger.getLogger(FeatureIndex.class.getName());

	/**
	 * to do.
	 */
	private SortedMap map;

	/**
	 * to do.
	 */
	private SortedMap inverseMap;

	//
	private Map<String, Counter> freqMap;

	/**
	 * to do.
	 */
	private int count;

	//
	private boolean readOnly;
	/**
	 * Constructs a <code>ngramIndex</code> object.
	 */
	public FeatureIndex()
	{
		this(false);
	} // end constructor


	/**
	 * Constructs a <code>ngramIndex</code> object.
	 */
	public FeatureIndex(boolean readOnly)
	{
		logger.debug("FeatureIndex is " + (readOnly ?  "read only" : "read/write"));
		map = new TreeMap();
		inverseMap = new TreeMap();
		freqMap = new HashMap<String, Counter>();
		this.readOnly = readOnly;
	} // end constructor

	//
	public int size()
	{
		return map.size();
	} // end size

	/**
	 * Returns the <i>index</i> of the specified term and adds
	 * the term to the ngramIndex if it is not present yet.
	 *
	 * @param term	the term.
	 * @return 			the <i>index</i> of the specified term.
	 */
	public int put(String term)
	{
		//logger.debug("ngramIndex.put : " + term + "(" + count + ")");
		Integer index = (Integer) map.get(term);

		if (readOnly)
		{
			if (index == null)
				return -1;

			return index.intValue();
		}

		if (index == null)
		{
			index = new Integer(count++);
			map.put(term, index);

			inverseMap.put(index, term);
		}

		Counter counter = freqMap.get(term);
		if (counter == null)
		{
			counter = new Counter();
			freqMap.put(term, counter);
		}
		counter.inc();

		return index.intValue();
	} // end get

	/**
	 * Returns the <i>index</i> of the specified term and adds
	 * the term to the ngramIndex if it is not present yet.
	 *
	 * @param term	the term.
	 * @return 			the <i>index</i> of the specified term.
	 */
	public int getIndex(String term)
	{
		//logger.debug("ngramIndex.get : " + term + "(" + count + ")");
		Integer index = (Integer) map.get(term);

		if (index == null)
			return -1;
		else return index;
	} // end get

	//
	public String getTerm(int i)
	{
		return (String) inverseMap.get(i);
	}
	//
	public Set termSet()
	{
		return map.keySet();
	} // end termSet

	/**
	 * Returns a <code>String</code> object representing this
	 * <code>Word</code>.
	 *
	 * @return a string representation of this object.
	 */
	public String toString()
	{
		StringBuffer sb = new StringBuffer();

		Iterator it = map.entrySet().iterator();
		while (it.hasNext())
		{
			Map.Entry me = (Map.Entry) it.next();
			Object f = me.getKey();
			sb.append(me.getValue());
			sb.append("\t");
			sb.append(f);
			sb.append("\t");
			sb.append(freqMap.get(f));

			sb.append("\n");
		}
		return sb.toString();
	} // end toTable

	/**
	 * Writes the feature ngramIndex into the specified
	 * output stream in a format suitable for loading
	 * into a <code>Map</code> using the
	 *
	 * @param out						a <code>Writer</code> object to
	 *											provide the underlying stream.
	 * @throws IOException	if writing this feature ngramIndex 
	 *											to the specified  output stream
	 *											throws an <code>IOException</code>.
	 */
	public void write(Writer out) throws IOException
	{
		PrintWriter pw = new PrintWriter(out);

		Iterator it = map.entrySet().iterator();
		logger.debug("writing ngramIndex " + map.entrySet().size());

		while (it.hasNext())
		{
			Map.Entry me = (Map.Entry) it.next();
			// index	term	freq
			Object f = me.getKey();
			pw.print(me.getValue() + "\t" + f);
			pw.print("\t");
			pw.println(freqMap.get(f).get());


		}
		pw.flush();
		pw.close();
	} // end write

	/**
	 * Reads the feature ngramIndex from the specified input stream.
	 * <p>
	 * This method processes input in terms of lines. A natural
	 * line of input is terminated either by a set of line
	 * terminator  characters (\n or \r or  \r\n) or by the end
	 * of the file. A natural line  may be either a blank line,
	 * a comment line, or hold some part  of a id-feature pair.
	 * Lines are read from the input stream until  end of file
	 * is reached.
	 * <p>
	 *  A natural line that contains only white space characters
	 * is  considered blank and is ignored. A comment line has
	 * an ASCII  '#' as its first non-white  space character;
	 * comment lines are also ignored and do not encode id-feature
	 * information.
	 * <p>
	 * The id contains all of the characters in the line starting
	 * with the first non-white space character and up to, but
	 * not  including, the first '\t'. All remaining characters
	 * on the line become part of  the associated feature string;
	 * if there are no remaining  characters, the feature is the
	 * empty string "".
	 *
	 * @param in						a <code>InputReader</code> object to
	 *											provide the underlying stream.
	 * @throws IOException	if reading this feature ngramIndex 
	 *											from the specified  input stream
	 *											throws an <code>IOException</code>.
	 */
	public void read(InputStreamReader in) throws IOException
	{
		long begin = System.currentTimeMillis();
		logger.info("reading vocabulary...");

		LineNumberReader lnr = new LineNumberReader(in);

		String line;
		String[] s;
		while ((line = lnr.readLine()) != null)
		{
			line = line.trim();
			if (!line.startsWith("#"))
			{
				s = line.split("\t");
				// term index	
				Integer index = new Integer(s[0]);
				Integer freq =  new Integer(s[2]);
				//if (freq.intValue() > 1)
				//{
					Object o = map.put(s[1], index);
					inverseMap.put(index, s[1]);
					if (o != null)
					{
						logger.warn(count + " returned " + o + ", " + s[1] + ", "  + s[0]);
					}
					// SETTARE COUNT
					count++;

				//}

			}
		}
		lnr.close();

		logger.debug(count + " terms read (" + map.size() + ")");
		long end = System.currentTimeMillis();
		logger.info("took " + (end - begin) + " ms to read " + count + " terms");

	} // end read

	//
	private class Counter
	{
		private int count;

		Counter()
		{
			count = 0;
		}

		//
		int get()
		{
			return count;
		}

		//
		void inc()
		{
			count++;
		}
	}
} // end class FeatureIndex