<%@ page import="com.launchdarkly.featureflag.util.LDUtil" %>
<%@ page import="com.launchdarkly.featureflag.util.LDConstants" %>
<%@ page contentType="text/xml"%>
<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>

<html>
    <head>
        <meta charset="UTF-8">
        <title>User Data Table</title>
        <style>
            table {
                width: 60%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th, td {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }
            th {
                background-color: #f2f2f2;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
        </style>
    </head>
    <body>
    <h2>Employee Information</h2>
    <table>
        <thead>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Department</th>
            <th>Email</th>
        </tr>
        </thead>
        <tbody>
        <tr>
            <td>101</td>
            <td>John Doe</td>
            <td>Engineering</td>
            <td>john.doe@example.com</td>
        </tr>
        <% if(LDUtil.getFlagStatusBySystemIdDefaultFalse(1L, LDConstants.PW_FIND_USER_DETAILS)) {%>
            <tr>
                <td>102</td>
                <td>Jane Smith</td>
                <td>Marketing</td>
                <td>jane.smith@example.com</td>
            </tr>
            <tr>
                <td>103</td>
                <td>Robert Johnson</td>
                <td>Sales</td>
                <td>robert.j@example.com</td>
            </tr>
        <% } %>
        <tr>
            <td>104</td>
            <td>Emily Davis</td>
            <td>HR</td>
            <td>emily.d@example.com</td>
        </tr>
        </tbody>
    </table>
    </body>
    </html>

