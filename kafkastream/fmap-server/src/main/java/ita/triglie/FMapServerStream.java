package ita.triglie;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.Topology;
import org.apache.kafka.streams.KeyValue;
import org.json.JSONObject;

import java.util.Properties;
import java.util.concurrent.CountDownLatch;

public class FMapServerStream {

    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "streams-FMap-server");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "kafkaserver:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());

        final StreamsBuilder builder = new StreamsBuilder();
        final MatcherFactory matcher = new MatcherFactory();

        builder.<String, String>stream("rds-signal")
            .map((k, v) -> {
                JSONObject jsonObject = new JSONObject(v);
                String province  = jsonObject.getString("province");
                Float  frequence = Float.parseFloat(jsonObject.getString("FM"));
                StationIdentifier sid = new StationIdentifier(frequence, province);
                String stationName = null;
                try {
                    stationName = matcher.match(sid);
                } catch (Exception e) {
                    e.printStackTrace();
                }
                System.out.println(stationName);
                return new KeyValue<String, String>(k, v.toUpperCase());
            })
            .to("rds-signal-output");

        final Topology topology = builder.build();
        final KafkaStreams streams = new KafkaStreams(topology, props);
        final CountDownLatch latch = new CountDownLatch(1);

        // attach shutdown handler to catch control-c
        Runtime.getRuntime().addShutdownHook(new Thread("streams-FMap-server-shutdown") {
            @Override
            public void run() {
                streams.close();
                latch.countDown();
            }
        });

        try {
            streams.start();
            latch.await();
        } catch (Throwable e) {
            System.exit(1);
        }
        System.exit(0);
    }
}
