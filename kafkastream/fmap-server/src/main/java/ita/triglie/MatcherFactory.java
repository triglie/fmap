package ita.triglie;


import java.util.*;

public class MatcherFactory {

    Map<String, List<String>> provinceMap = new HashMap<String, List<String>>() {{
        put("Catania", Arrays.asList("catania", "siracusa", "ragusa", "enna", "caltanissetta"));
        put("Palermo", Arrays.asList("palermo", "trapani", "agrigento"));
        put("Messina", Arrays.asList("messina"));
    }};

    public String match(StationIdentifier identifier) throws Exception {
        Matcher matcher = identifier.hasProgrammeIdentifier()
                ? new NationalMatcher()
                : new ProvinceMatcher(this.getNearestProvinceWithStationData(identifier.getProvince()));
        return matcher.match(identifier);
    }

    private String getNearestProvinceWithStationData(String province) throws Exception {
        for (String provinceWithStationData : provinceMap.keySet()) {
            List<String> nearProvinces = provinceMap.get(provinceWithStationData);
            if (nearProvinces.contains(province.toLowerCase()))
                return provinceWithStationData;
        }
        throw new Exception("Province not found");
    }

}
