package org.fbk.cit.hlt.dirha;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsonorg.JsonOrgModule;
import org.apache.log4j.Logger;
import org.eclipse.jetty.client.api.ContentResponse;
import org.eclipse.jetty.client.api.Request;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

/**
 * Created by admin on 4/20/15.
 */
public class TheWikiMachineClient {

    public static final Logger logger = Logger.getLogger(TheWikiMachineClient.class.getName());

    private final String TWM_ENDPOINT;
    private final String APP_ID;
    private final String APP_KEY;
    private final String DEFAULT_LANGUAGE = "it";
    private final Map<String, String> API_PARAMS;

    public static final String SOCCER_WORDS = " calcio ronaldo attaccante beckham gol totti";

    public TheWikiMachineClient() throws IOException {
        Properties prop = new Properties(  );
        prop.load( getClass( ).getClassLoader( ).getResourceAsStream( "secrets.properties" ) );
        TWM_ENDPOINT = prop.getProperty( "TWM_ENDPOINT" );
        APP_ID = prop.getProperty( "APP_ID" );
        APP_KEY = prop.getProperty( "APP_KEY" );

        API_PARAMS = new HashMap<String, String>() {{
            put("app_id", APP_ID);
            put("app_key", APP_KEY);
            put("lang", DEFAULT_LANGUAGE);
            put("min_weight", "0.01");
        }};
    }

    public static void main(String[] args) throws Exception {
        String text = "Ha giocato in massima serie portoghese dal 1998 al 2000";
        TheWikiMachineClient twmClient = new TheWikiMachineClient();
        JSONObject response = twmClient.linkText(text, true);
        JSONArray entities = twmClient.extractEntities(response, true);
        System.out.println(entities.toString());
    }

    public JSONArray extractEntities(JSONObject twmResponse, boolean disambiguation) throws JSONException {
        JSONArray entities = new JSONArray();
        JSONArray keywords = twmResponse.getJSONObject("annotation").getJSONArray("keyword");
        for (int i = 0; i < keywords.length(); i++) {
            JSONObject keyword = keywords.getJSONObject(i);
            logger.debug(keyword);
            JSONObject entity = new JSONObject();
            entity.put("score", keyword.get("rel"));
            if (disambiguation) {
                if (keyword.has("sense")) {
                    entity.put("uri", "http://it.wikipedia.org/wiki/" + keyword.getJSONObject("sense").get("page"));
                }
                JSONArray types = new JSONArray();
//                Replace stolen URIs
                JSONArray classes = keyword.getJSONArray("class");
                for (int j = 0; j < classes.length(); j++) {
                    JSONObject typeObject = classes.getJSONObject(j);
                    String type = typeObject.getString("url");
                    String DBpediaType = type.replace("www.airpedia.org/ontology/class", "dbpedia.org/ontology");
                    types.put(DBpediaType);
                }
            }
            JSONArray nGrams = keyword.getJSONArray("ngram");
            for (int k = 0; k < nGrams.length(); k++) {
                JSONObject nGram = nGrams.getJSONObject(k);
                entity.put("chunk", nGram.get("form"));
                JSONObject span = nGram.getJSONObject("span");
                entity.put("start", span.get("start"));
                entity.put("end", span.get("end"));
                entities.put(entity);
            }
        }
        return entities;
    }

    public JSONObject linkText(String text, boolean disambiguation) throws Exception {
//      Constrain the context to the soccer domain
        API_PARAMS.put("text", text + SOCCER_WORDS);
        if (disambiguation) {
            API_PARAMS.put("disambiguation", "1");
            API_PARAMS.put("class", "1");
        } else {
            API_PARAMS.put("disambiguation", "0");
            API_PARAMS.put("class", "0");
        }
        org.eclipse.jetty.client.HttpClient client = new org.eclipse.jetty.client.HttpClient();
        client.start();
        Request request = client.newRequest(TWM_ENDPOINT);
        for (String paramName : API_PARAMS.keySet()) {
            request.param(paramName, API_PARAMS.get(paramName));
        }
        ContentResponse response = request.send();
        client.stop();
        ObjectMapper mapper = new ObjectMapper();
        mapper.registerModule(new JsonOrgModule());
        return mapper.readValue(response.getContent(), JSONObject.class);
    }

}
