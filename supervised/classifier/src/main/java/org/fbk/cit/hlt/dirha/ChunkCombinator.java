package org.fbk.cit.hlt.dirha;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Created by admin on 4/17/15.
 * TODO filter stopwords
 * TODO 5. Merge chunks with overlapping tokens, e.g., 'massima serie' and 'serie portoghese' = 'massima serie portoghese'
 */
public class ChunkCombinator {

    private final TheWikiMachineClient twm = new TheWikiMachineClient();
    private final TextProRunner tpr = new TextProRunner();

    public ChunkCombinator() {
    }

    public static void main(String[] args) throws Exception {
        String sentence = "Ha giocato per quattro anni nella massima serie scozzese con il Dundee.";
        ChunkCombinator combinator = new ChunkCombinator();
        Set<String> disambiguated = combinator.getTheWikiMachineChunks(sentence, true);
        Set<String> nGrams = combinator.getTheWikiMachineChunks(sentence, false);
        Set<String> nounPhrases = combinator.getTextProNPChunks(sentence);
        System.out.println(combinator.combineChunks(disambiguated, nGrams, nounPhrases));
        System.exit(0);
    }


    public Set<String> getTheWikiMachineChunks(String sentence, boolean disambiguation) throws Exception {
        Set<String> twmChunks = new HashSet<>();
        JSONObject response = twm.linkText(sentence, disambiguation);
        JSONArray chunks = twm.extractEntities(response, disambiguation);
        for (int i = 0; i < chunks.length(); i++) {
            JSONObject link = chunks.getJSONObject(i);
            String chunk = link.getString("chunk");
            twmChunks.add(chunk);
        }
        return twmChunks;
    }


    public Set<String> getTextProNPChunks(String sentence) throws IOException {
        List<String> chunks = tpr.runTextPro(sentence);
        return tpr.extractNPChunks(chunks);
    }

    public Set<String> combineChunks(Set<String> disambiguated, Set<String> nGrams, Set<String> nounPhrases) {
//        Prune n-grams from links
        Set<String> toRemove = new HashSet<>();
        for (String dis : disambiguated) {
            for (String nGram : nGrams) {
                if (nGram.contains(dis) || dis.contains(nGram)) {
                    toRemove.add(nGram);
                }
            }
        }
        nGrams.removeAll(toRemove);
//        Prune TextPro chunks from links
        toRemove = new HashSet<>();
        for (String dis : disambiguated) {
            for (String np : nounPhrases) {
                if (np.contains(dis) || dis.contains(np)) {
                    toRemove.add(np);
                }
            }
        }
        nounPhrases.removeAll(toRemove);
//        Prune TextPro chunks from n-grams
        toRemove = new HashSet<>();
        for (String nGram : nGrams) {
            for (String np : nounPhrases) {
                if (np.contains(nGram) || nGram.contains(np)) {
                    toRemove.add(np);
                }
            }
        }
        nounPhrases.removeAll(toRemove);

        nounPhrases.addAll(nGrams);
        nounPhrases.addAll(disambiguated);
        return nounPhrases;
    }
}
