package ita.triglie;

import java.io.IOException;
import java.io.Reader;
import java.io.StringReader;
import java.util.HashMap;
import java.util.Map;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVRecord;

public class ProvinceMatcher extends Matcher {

    private final Map<String, String> filenames = new HashMap<String, String>() {{
        put("CATANIA", "Resources/fm-station-map-catania.csv");
        put("PALERMO", "Resources/fm-station-map-palermo.csv");
        put("MESSINA", "Resources/fm-station-map-messina.csv");
    }};

    public ProvinceMatcher(String province) {
        super();
        loadInfo(filenames.get(province.toUpperCase()).toString());
    }

    @Override
    protected void loadInfo(String filename) {
        String csv = super.createStringCSV(filename);
        Reader in = new StringReader(csv.toString());
        try {
            for (CSVRecord record : CSVFormat.DEFAULT.parse(in)) {
                for (String field : record) {
                    try {
                        float fm = Float.parseFloat(field);
                        super.listFM.add(fm);
                    } catch(Exception e) {
                        super.radioNames.add(field);
                    }
                }
            }
        } catch (IOException e) {
            System.exit(-1);
            e.printStackTrace();
        }
    }
}
