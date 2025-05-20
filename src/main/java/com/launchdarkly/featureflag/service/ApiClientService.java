package com.launchdarkly.featureflag.service;

import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class ApiClientService implements IApiClient{

    private final RestTemplate restTemplate = new RestTemplate();

    @Override
    public String fetchData(String userId) {
        String url = "https://jsonplaceholder.typicode.com/posts/1";
        ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
        return response.getBody();
    }
}
