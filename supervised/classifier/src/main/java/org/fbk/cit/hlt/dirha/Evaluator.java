package org.fbk.cit.hlt.dirha;

import org.apache.commons.cli.*;
import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;

import java.io.*;
import java.text.DecimalFormat;
import java.util.*;
import java.util.List;

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
 * Date: 11/26/13
 * Time: 4:03 PM
 * To change this template use File | Settings | File Templates.
 */
public class Evaluator {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>Evaluator</code>.
	 */
	static Logger logger = Logger.getLogger(Evaluator.class.getName());
	private File goldFile;
	private File testFile;

	protected static DecimalFormat df = new DecimalFormat("0.00");

	Evaluation frameEvaluation;
	Evaluation roleEvaluation;

    FeatureIndex frameLabels;
    FeatureIndex roleLabels;

    ConfusionMatrix rolesConfusionMatrix;
    ConfusionMatrix framesConfusionMatrix;

    public Evaluator(File goldFile, File testFile, File frameLabelsFile, File roleLabelsFile) throws IOException {
		this.goldFile = goldFile;
		this.testFile = testFile;

        frameLabels = InputReader.ReadFeatureIndex( frameLabelsFile, false );
        roleLabels = InputReader.ReadFeatureIndex( roleLabelsFile, false );

        ClassifierResults.FrameLabelList = frameLabels;
        ClassifierResults.RoleLabelList = roleLabels;

        Map<Integer, Sentence> goldSentences = read(goldFile);
        Map<Integer, Sentence> testSentences = read(testFile);

		logger.info( "gold: " + goldFile );
		logger.info("test: " + testFile);
		logger.debug("Total sentences: gold = " + goldSentences.size() + ", test = " + testSentences.size());

		frameEvaluation = new Evaluation();
		roleEvaluation = new Evaluation();

        rolesConfusionMatrix = new ConfusionMatrix( roleLabels.size( ) );
        framesConfusionMatrix = new ConfusionMatrix( frameLabels.size( ) );

		for (int testId: testSentences.keySet()) {
            logger.info("============ Evaluating test sentence #" + testId + "... ============");
            Sentence testSentence = testSentences.get(testId);
            logger.debug("Test = " + testSentence);
            Sentence goldSentence;
            if (goldSentences.containsKey(testId)) {
                goldSentence = goldSentences.get(testId);
                logger.debug("Gold = " + goldSentence);
            }
            else {
                logger.warn("No gold found for test sentence #" + testId + ": " + testSentence + " Skipping ...");
                continue;
            }
            evaluateFrame(goldSentence, testSentence, frameEvaluation, framesConfusionMatrix);
            evaluateRole(goldSentence, testSentence, roleEvaluation, rolesConfusionMatrix);
        }

		System.out.println("gold: " + goldFile.getAbsolutePath());
		System.out.println("test: " + testFile.getAbsolutePath());

        System.out.println("Micro averaged statistics");
		System.out.println("\ttp\tfp\tfn\ttot\tP\tR\tF1");
		System.out.println("frm\t" + frameEvaluation);
		System.out.println("rol\t" + roleEvaluation);

        System.out.println("Macro averaged statistics");
        System.out.println("\n***  Roles Confusion Matrix  ***");
        System.out.println(roleLabels);
        System.out.println(rolesConfusionMatrix.toTable( ));

        System.out.println("\n***  Frames Confusion Matrix  ***");
        System.out.println(frameLabels);
        System.out.println(framesConfusionMatrix.toTable( ));
    }

	public Evaluation getRoleEvaluation() {
		return roleEvaluation;
	}

	public Evaluation getFrameEvaluation() {
		return frameEvaluation;
	}

	// todo: comparison must be done based on the type b-lu, b-device... otherwise I compare b-lu with b-device...
	void evaluateRole(Sentence goldSentence, Sentence testSentence, Evaluation frameEvaluation, ConfusionMatrix confusionMatrix ) {
        logger.info("----------- Evaluating roles... -----------");
        String goldId = goldSentence.getId();
		Set<String> gold = goldSentence.getFrames( );
		//logger.debug(i + "\tgold\t" + goldSentenceFrames);
		String testId = testSentence.getId();
		Set<String> test = testSentence.getFrames( );
        logger.trace("Test getFrames: " + test);
        String testFrame = null;
        if (!test.isEmpty()) {
            //		Only consider the first test frame
            testFrame = test.iterator().next();
        }
        else {
            logger.warn("No getFrames for test sentence #" + testId);
        }
		if (test.size() > 1) {
            logger.warn("More than 1 frame detected in test sentence #" + testId + ". Evaluating only [" + testFrame + "] roles...");
		}
		Iterator<String> goldIterator = gold.iterator();
		for (int i = 0; goldIterator.hasNext(); i++) {
			String goldFrame = goldIterator.next();

			List<Role> goldRoleList = goldSentence.getRoleList(goldFrame);
            if (goldRoleList == null) {
                logger.warn("No annotated roles for gold sentence #" + goldId);
                goldRoleList = new ArrayList<>();
            }
			// If the test frame is wrong, it doesn't mean the roles are wrong too (as many overlap across getFrames), so evaluate less strictly
            List<Role> testRoleList = testSentence.getRoleList(testFrame);
            if (testRoleList == null) {
                logger.warn("No annotated roles for test sentence #" + testId);
                testRoleList = new ArrayList<>();
            }
			logger.debug("Gold frame = [" + goldFrame + "], gold roles = " + goldRoleList);
			logger.debug("Test frame = [" + testFrame + "], test roles = " + testRoleList);
			for (int j = 0; j < goldRoleList.size(); j++) {
				Role goldRole = goldRoleList.get(j);
                String goldRoleValue = goldRole.getValue();
                String goldRoleName = goldRole.getName();
//                Skip LUs
//                if (goldRoleName.equalsIgnoreCase("lu")) {
//                    continue;
//                }

//                Strict checking
//				if (testRoleList.contains(goldRole)) {
//
//					frameEvaluation.incTp();
//					logger.warn("TP\t" + frameEvaluation.getTp() + "\t" + goldId + "\t<" + goldRole + ">\t" + test + "(" + testRoleList + ")");
//				}
//				else {
//					frameEvaluation.incFn();
//					logger.warn("FN\t" + frameEvaluation.getFn() + "\t" + goldId + "\t<" + goldRole + ">\t" + test + "(" + testRoleList + ")");
//				}
//                Partial checking
                int partialMatches = 0;
                for (Role testRole : testRoleList) {
                    String testRoleValue = testRole.getValue();
                    String testRoleName = testRole.getName();

                    if (goldRoleValue.contains(testRoleValue)) {
                        partialMatches += 1;
                        logger.debug("Current gold role value = [" + goldRoleValue + "], test = [" + testRoleValue + "]. At least a partial match");
                        confusionMatrix.AddResult( roleLabels.getIndex( testRoleName ),
                                                   roleLabels.getIndex( goldRoleName ) );

                        if (goldRoleName.equalsIgnoreCase(testRoleName)) {
                            logger.debug("Gold sentence #" + goldId + ", gold role: " + goldRoleName + ", test role: " + testRoleName);
                            frameEvaluation.incTp();
                            logger.warn("+1 roles TP, total = " + frameEvaluation.getTp());
                        }
                        else {
                            logger.warn("Gold sentence #" + goldId + ", gold role: " + goldRoleName + ", test role: " + testRoleName);
                            frameEvaluation.incFp();
                            logger.warn("+1 roles FP, total = " + frameEvaluation.getTp());
                            frameEvaluation.incFn();
                            logger.warn("+1 roles FN, total = " + frameEvaluation.getFn());
                        }
                    }
                }
                if (partialMatches == 0) {
                    logger.warn("Gold role value [" + goldRoleValue + "] not in test roles " + testRoleList);
                    frameEvaluation.incFn();
                    logger.warn("+1 roles FN, total = " + frameEvaluation.getFn());
                    confusionMatrix.AddResult( roleLabels.getIndex( "O" ),
                                               roleLabels.getIndex( goldRoleName ) );
                }
			}

//            Check for any FP seen by the classifier that are not in the gold
            for (Role testRole : testRoleList) {
                int partialMatches = 0;
                String testRoleValue = testRole.getValue();
                for (Role goldRole : goldRoleList) {
                    String goldRoleValue = goldRole.getValue();
                    if (goldRoleValue.contains(testRoleValue)) {
                        partialMatches += 1;
                    }
                }
                if (partialMatches == 0) {
                    logger.warn("Test role " + testRole + " not in gold roles " + goldRoleList);
                    frameEvaluation.incFp();
                    logger.warn("+1 FP, total = " + frameEvaluation.getTp());
					confusionMatrix.AddResult( roleLabels.getIndex( testRole.getName( ) ),
											   roleLabels.getIndex( "O" ) );
                }
            }

////                Strict checking
//			for (int j = 0; j < testRoleList.size(); j++) {
//				Role testRole = testRoleList.get(j);
//				if (!goldRoleList.contains(testRole)) {
//					frameEvaluation.incFp();
//					logger.warn("FP\t" + frameEvaluation.getFp() + "\t" + goldId + "\t(" + goldRoleList + ")\t" + test + "<" + testRole + ">");
//				}
//			}
		}
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
			if (role.getName().startsWith("b-")) {
				//logger.debug("a\t\t" + role);
				prevRole = new Role(role);
				list.add(prevRole);
			}
			else if (role.getName().startsWith("i-")) {
				//logger.debug("b\t\t" + role);
				//prevRole.setName(prevRole.getValue().substring(2, prevRole.getName().length()));
				if (prevRole==null) {
					prevRole = new Role(role);
				}
				prevRole.setValue(prevRole.getValue() + " " + role.getValue());
			}
		}
		//logger.debug("after\t" + list);
		return list;
	}

	void evaluateFrame(Sentence goldSentence, Sentence testSentence, Evaluation frameEvaluation, ConfusionMatrix confusionMatrix) {
        logger.info("----------- Evaluating getFrames... -----------");
		String goldId = goldSentence.getId();

        Set<String> test = testSentence.getFrames( );
        Set<String> gold = goldSentence.getFrames( );

        String predictedFrame = test.size() == 1 ? test.iterator().next() : "O";
        String actualFrame = gold.iterator().next();

        confusionMatrix.AddResult( frameLabels.getIndex( predictedFrame ), frameLabels.getIndex( actualFrame ) );

		Iterator<String> goldIterator = gold.iterator();
		for (int i = 0; goldIterator.hasNext(); i++) {
			String goldFrame = goldIterator.next();
            logger.debug("Gold sentence #" + goldId + ", gold frame [" + goldFrame + "], test getFrames " + test);

			if (test.contains(goldFrame)) {
                frameEvaluation.incTp();
                logger.warn("+1 frame TP, total = " + frameEvaluation.getTp());

                confusionMatrix.AddResult( frameLabels.getIndex( goldFrame ), frameLabels.getIndex( goldFrame ) );
            }
			else {
				frameEvaluation.incFn();
                logger.warn("+1 frame FN, total = " + frameEvaluation.getTp());
            }
		}

		Iterator<String> testIterator = test.iterator();
		for (int i = 0; testIterator.hasNext(); i++) {
            String testFrame = testIterator.next();
            if (!gold.contains(testFrame)) {
                frameEvaluation.incFp();
                logger.warn("+1 frame FP, total = " + frameEvaluation.getTp());
            }
		}
	}

	/*class Role {
		private int id;
		private String name;
		private String value;

		Role(Role role) {
			this.id = role.getId();
			this.name = role.getName();
			this.value = role.getValue();
		}

		Role(int id, String name, String value) {
			this.id = id;
			this.name = name;
			this.value = value;
		}

		void setId(int id) {
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

		int getId() {
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
		public String toTable() {
			return "Role{" +
					"id=" + id +
					", name='" + name + '\'' +
					", value='" + value + '\'' +
					'}';
		}
	}   */

	class Evaluation {
		private int tp;
		private int fp;
		private int fn;

		Evaluation() {
			this(0, 0, 0);
		}

		Evaluation(int tp, int fp, int fn) {
			this.tp = tp;
			this.fp = fp;
			this.fn = fn;
		}

		void incTp() {
			tp++;
		}

		void incFp() {
			fp++;
		}

		void incFn() {
			fn++;
		}


		int getFn() {
			return fn;
		}

		void setFn(int fn) {
			this.fn = fn;
		}

		int getFp() {
			return fp;
		}

		void setFp(int fp) {
			this.fp = fp;
		}

		int getTp() {
			return tp;
		}

		void setTp(int tp) {
			this.tp = tp;
		}

		double precision() {
			return (double) tp / (tp + fp);
		}

		double recall() {
			return (double) tp / (tp + fn);
		}

		double f1() {
			return (2 * precision() * recall()) / (precision() + recall());
		}

		@Override
		public String toString() {
			return tp + "\t" + fp + "\t" + fn + "\t" + (tp + fn) + "\t" + df.format(precision()) + "\t" + df.format(recall()) + "\t" + df.format(f1());
		}
	}

/*	class Sentence {
		private Map<String, List<Role>> frameMap;
		private int id;


		Sentence(int id) {
			this.id = id;
			frameMap = new HashMap<String, List<Role>>();
		}

		int getId() {
			return id;
		}

		public Set<String> getFrames() {
			return frameMap.keySet();
		}

		public void addMeasure(int id, String frame, String role, String value) {
			//logger.debug("adding role " + frame + "\t" + role + "\t" + value);
			if (frame.length() == 0) {
				return;
			}
			List<Role> roleList = frameMap.get(frame);
			if (roleList == null) {
				roleList = new ArrayList<Role>();
				frameMap.put(frame, roleList);
			}
			roleList.addMeasure(new Role(id, role, value));
		}

		public List<Role> getRoleList(String frame) {
			return frameMap.get(frame);
		}

		@Override
		public String toTable() {
			return "Sentence{" +
					"frameMap=" + frameMap +
					", id=" + id +
					'}';
		}
	}  */

	private Map<Integer, Sentence> read(File fin) throws IOException {
		LineNumberReader lr = new LineNumberReader(new InputStreamReader(new FileInputStream(fin), "UTF-8"));

		String line = null;
		Map<Integer, Sentence> sentenceMap = new HashMap<>();
		String sid = null;
		int count = 0;
		Sentence sentence = null;
		while ((line = lr.readLine()) != null) {

			String[] s = line.split("\t", -1);
			if (s.length > 5) {

				if (sid == null) {
					sid = s[0];
					sentence = new Sentence(sid);
				}
				if (!s[0].equalsIgnoreCase(sid)) {
					sentenceMap.put(Integer.parseInt(sid), sentence);
					sid = s[0];
					sentence = new Sentence(sid);
				}
				if (!s[6].trim().equalsIgnoreCase("O")) {
					ClassifierResults res = ClassifierResults.fromTSV( s, 2 );
                    sentence.add(s[0], res.getFrame(), res.getRole(), res.getToken());
				}

			}

		}
		sentenceMap.put(Integer.parseInt(sid), sentence);
		return sentenceMap;
	}

	public void write(File f) throws IOException {
		PrintWriter pw = new PrintWriter(new BufferedWriter(new OutputStreamWriter(new FileOutputStream(f), "UTF-8")));

		pw.println("gold\t" + goldFile.getName());
		pw.println("test\t" + testFile.getName() + "\n");
		pw.println("\ttp\tfp\tfn\ttot\tP\tR\tF1");
		pw.println("frm\t" + frameEvaluation);
		pw.println("rol\t" + roleEvaluation);
        pw.println("\n*** Roles Confusion Matrix ***");
        pw.println(rolesConfusionMatrix .toTable( ));
        pw.println("\n*** Frames Confusion Matrix ***");
        pw.println(framesConfusionMatrix.toTable( ));
        pw.close( );

        File rolesCf = new File( f.getAbsolutePath( ) + ".roles.confusion.csv" );
        pw = new PrintWriter( new BufferedWriter( new OutputStreamWriter( new FileOutputStream( rolesCf ), "UTF-8" ) ) );
        pw.write( rolesConfusionMatrix.toCSV( ClassifierResults.RoleLabelList ) );
        pw.close( );

        File framesCf = new File( f.getAbsolutePath( ) + ".frames.confusion.csv" );
        pw = new PrintWriter( new BufferedWriter( new OutputStreamWriter( new FileOutputStream( framesCf ), "UTF-8" ) ) );
        pw.write( framesConfusionMatrix.toCSV( ClassifierResults.FrameLabelList ) );
        pw.close( );
    }
	public static void main(String[] args) {
		String logConfig = System.getProperty("log-config");
		if (logConfig == null) {
			logConfig = "log-config.txt";
		}
		PropertyConfigurator.configure(logConfig);

		Options options = new Options();
		try {
			Option goldFileOpt = OptionBuilder.withArgName("file").hasArg().withDescription("file from which to read the gold file in tsv format").isRequired().withLongOpt("gold").create("g");
			Option testFileOpt = OptionBuilder.withArgName("file").hasArg().withDescription("file from which to read the test file in tsv format").isRequired().withLongOpt("test").create("t");
            Option roleLabelFileOpt = OptionBuilder.withArgName("file").hasArg().withDescription("file from which to read the gold file in tsv format").isRequired().withLongOpt("role-labels").create("r");
            Option frameLabelFileOpt = OptionBuilder.withArgName("file").hasArg().withDescription("file from which to read the gold file in tsv format").isRequired().withLongOpt("frame-labels").create("f");

			options.addOption("h", "help", false, "print this message");
			options.addOption("v", "version", false, "output version information and exit");

			options.addOption( goldFileOpt );
			options.addOption( testFileOpt );
            options.addOption( roleLabelFileOpt );
            options.addOption( frameLabelFileOpt );

			CommandLineParser parser = new PosixParser();
			CommandLine line = parser.parse(options, args);

			File goldFile = new File(line.getOptionValue("gold"));
			File testFile = new File(line.getOptionValue("test"));
            File frameLabels = new File(line.getOptionValue( "frame-labels" ));
            File roleLabels = new File(line.getOptionValue( "role-labels" ));

            Evaluator eval = new Evaluator( goldFile, testFile, frameLabels, roleLabels );
            eval.write( new File( "/tmp/evaluation" ) );
        } catch (ParseException e) {
			// oops, something went wrong
			System.out.println("Parsing failed: " + e.getMessage() + "\n");
			HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp(400, "java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.Evaluator", "\n", options, "\n", true);
		} catch (IOException e) {
			logger.error(e);
		}

	}
}